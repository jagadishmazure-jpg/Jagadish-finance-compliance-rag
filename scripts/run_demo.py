"""Demo: answer a regression question, then show a refusal.

Run:  python3 scripts/run_demo.py
Stdlib only. No network, no credentials, synthetic data only.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from compliance_rag.corpus import REGRESSION_SET, load_corpus
from compliance_rag.qa import answer_question
from compliance_rag.retrieval import Retriever
from compliance_rag.redaction import redact


def main() -> None:
    retriever = Retriever(load_corpus())
    question = "How long must identity verification records be kept after an account closes?"
    answer = answer_question(question, retriever)
    print(f"Question: {question}")
    print(f"Status: {answer.status} (confidence {answer.confidence:.3f})")
    for claim in answer.claims:
        print(f"Citation [{claim.passage_id}]: {redact(claim.text)}")
    print()
    refused = answer_question("What is the capital of France?", retriever)
    print(f"Unrelated question -> status: {refused.status}, "
          f"claims: {len(refused.claims)}, escalate: {refused.escalate_to_human}")
    print(f"Reason: {refused.refusal_reason}")
    print()
    print("Regression set (n=6):")
    for question, expected in REGRESSION_SET:
        got = answer_question(question, retriever)
        cited = {c.source_id for c in got.claims}
        print(f"  [{got.status:12s}] expected {expected} "
              f"cited={sorted(cited)} :: {question[:60]}")


if __name__ == "__main__":
    main()
