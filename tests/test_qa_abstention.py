"""Question-to-cited-answer + trust-boundary tests."""

from compliance_rag.corpus import REGRESSION_SET, load_corpus
from compliance_rag.qa import answer_question
from compliance_rag.retrieval import Retriever


def _retriever():
    return Retriever(load_corpus())


def test_answered_question_has_citations_for_every_claim():
    answer = _retriever_answer("How long must identity verification records be kept?")
    assert answer.status == "answered"
    assert answer.claims
    assert answer.citations
    for claim in answer.claims:
        assert claim.passage_id in answer.citations
        assert claim.text in _passage_text(claim.passage_id)


def _retriever_answer(question):
    return answer_question(question, _retriever())


def _passage_text(passage_id):
    for chunk in load_corpus():
        if chunk.chunk_id == passage_id:
            return chunk.text
    raise AssertionError(f"unknown passage {passage_id}")


def test_every_claim_names_its_source_passage():
    answer = _retriever_answer("How often must customer risk ratings be reviewed?")
    assert answer.claims
    assert all(c.source_id and c.passage_id for c in answer.claims)


def test_abstention_on_weak_retrieval_gives_no_claims():
    """PROOF: weak retrieval -> refusal, not a hallucinated answer."""
    answer = answer_question("What is the capital of France?", _retriever())
    assert answer.status == "abstained"
    assert answer.claims == []
    assert answer.citations == []
    assert answer.escalate_to_human is True
    assert answer.refusal_reason


def test_abstention_on_empty_question():
    answer = answer_question("   ", _retriever())
    assert answer.status == "abstained"
    assert answer.claims == []


def test_abstention_on_no_passage_retrieved():
    answer = answer_question("zxqv jumbled nonsense words", _retriever())
    assert answer.status == "abstained"
    assert answer.escalate_to_human is True


def test_escalation_zone_flags_human_review():
    """A borderline score produces a draft flagged for review, not a final answer."""
    # A vague query that shares some words but is not a regression question.
    answer = answer_question("records training review", _retriever(),
                             answer_threshold=0.99, abstain_threshold=0.05)
    assert answer.status in ("needs_review", "abstained")
    if answer.status == "needs_review":
        assert answer.escalate_to_human is True


def test_regression_set_citations_match_known_good_sources():
    """Regression checks (n=6, hand-written): each question's known-good
    source must appear among its citations, or the answer must abstain
    rather than cite the wrong source."""
    for question, expected_source in REGRESSION_SET:
        answer = _retriever_answer(question)
        if answer.status == "answered":
            assert expected_source in {c.source_id for c in answer.claims}, question
        else:
            assert answer.status in ("needs_review", "abstained")
            assert answer.escalate_to_human is True


def test_regression_set_majority_answered():
    answered = sum(
        1 for q, _ in REGRESSION_SET
        if _retriever_answer(q).status == "answered")
    # Honest bar on a 6-question set: at least 4 answered, rest escalated.
    assert answered >= 4
