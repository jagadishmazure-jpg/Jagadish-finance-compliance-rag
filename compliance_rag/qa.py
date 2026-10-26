"""Question-to-cited-answer flow with trust boundaries.

Trust boundaries (all tested):
- ANSWERED: top retrieval score >= ``answer_threshold``. Every factual
  claim names its source passage; a claim is never invented -- each claim's
  text is an excerpt of a retrieved passage.
- NEEDS_REVIEW: score between ``abstain_threshold`` and
  ``answer_threshold``. A draft is produced, but it is flagged for human
  review and must not be treated as a final answer.
- ABSTAINED: score below ``abstain_threshold`` (or no passage at all).
  The system returns NO claims and NO answer text, only the refusal and
  an escalation flag. Refusing is the correct behaviour here; a confident
  sounding guess would be a hallucination.

Thresholds are defaults, not tuned values: they were picked so the
6-question regression set separates cleanly, and docs/limitations.md
says so plainly.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from compliance_rag.retrieval import Retriever, ScoredPassage


@dataclass(frozen=True)
class Claim:
    """One factual claim, always tied to one retrieved passage."""
    text: str
    passage_id: str
    source_id: str


@dataclass
class Answer:
    status: str  # "answered" | "needs_review" | "abstained"
    claims: list[Claim] = field(default_factory=list)
    citations: list[str] = field(default_factory=list)
    confidence: float = 0.0
    top_passage: ScoredPassage | None = None
    escalate_to_human: bool = False
    refusal_reason: str = ""


def _excerpt(passage: ScoredPassage) -> str:
    # Exact prefix of the passage (no ellipsis stitching), so a claim's
    # text is always verifiably contained in its cited passage.
    return passage.chunk.text[:240]


def answer_question(question: str, retriever: Retriever, top_k: int = 3,
                    answer_threshold: float = 0.35,
                    abstain_threshold: float = 0.20) -> Answer:
    if not question or not question.strip():
        return Answer(status="abstained", escalate_to_human=True,
                      refusal_reason="empty question: nothing to retrieve")
    results = retriever.search(question, top_k=top_k)
    if not results:
        return Answer(status="abstained", escalate_to_human=True,
                      refusal_reason="no passage retrieved for this question")
    top = results[0]
    if top.score < abstain_threshold:
        return Answer(status="abstained", confidence=top.score,
                      top_passage=top, escalate_to_human=True,
                      refusal_reason=(
                          f"best retrieval score {top.score:.3f} is below the "
                          f"abstention threshold {abstain_threshold}; no passage "
                          "supports an answer, so no answer is given"))
    claims = [Claim(text=_excerpt(p), passage_id=p.chunk.chunk_id,
                    source_id=p.chunk.source_id)
              for p in results if p.score >= abstain_threshold]
    citations = [c.passage_id for c in claims]
    if top.score < answer_threshold:
        return Answer(status="needs_review", claims=claims, citations=citations,
                      confidence=top.score, top_passage=top,
                      escalate_to_human=True,
                      refusal_reason=(
                          "retrieval confidence is below the answer threshold; "
                          "draft only, human review required"))
    return Answer(status="answered", claims=claims, citations=citations,
                  confidence=top.score, top_passage=top)
