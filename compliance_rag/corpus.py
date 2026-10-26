"""Synthetic regulation corpus and regression set.

EVERY document here is invented for this demo. The firm "Bramley Bank" is
fictional (no such bank was found as a real institution; the name is used
only as an invented brand for this scaffold). The "codes" below are
invented text, not real regulations, and their numbers (years, days,
thresholds) are made up. They exist so retrieval, citation, and
abstention can be tested end to end without touching real legal text.
"""

from __future__ import annotations

from compliance_rag.chunking import Chunk, chunk_text

# source_id -> invented document text. Keep each document short so chunks
# stay readable and citations stay checkable by hand.
_DOCUMENTS: dict[str, str] = {
    "BB-CDD-01": (
        "Bramley Bank Customer Due Diligence Standard. Before opening an account, "
        "staff must verify the customer's identity from an approved document and "
        "record the customer's full name, date of birth, and residential address. "
        "Where the customer acts for another person, staff must also record that "
        "person's identity. Records of identity verification must be retained for "
        "seven years after the account is closed."
    ),
    "BB-REC-02": (
        "Bramley Bank Record Retention Standard. Compliance records must be stored "
        "in a form that can be retrieved within five business days of a request. "
        "Records relating to closed accounts must be retained for seven years after "
        "closure, and records of staff training must be retained for three years "
        "after the training date. Records must not be destroyed before the end of "
        "the applicable retention period, even if storage space is limited."
    ),
    "BB-AML-03": (
        "Bramley Bank Suspicious Activity Standard. Staff who notice activity that "
        "does not match a customer's known profile must raise an internal report "
        "within two business days. The report must describe the activity, the dates "
        "involved, and the reason it appears unusual. Staff must not inform the "
        "customer that a report has been raised. A compliance officer must review "
        "each internal report within five business days and decide whether to "
        "escalate it for external filing."
    ),
    "BB-KYC-04": (
        "Bramley Bank Ongoing Monitoring Standard. Customer risk ratings must be "
        "reviewed at least once every twelve months, and sooner if the customer's "
        "circumstances change materially. A customer whose risk rating rises must "
        "receive enhanced monitoring, which includes a review of transactions over "
        "the previous six months. The outcome of each review must be recorded with "
        "the reviewer's name and the date of the review."
    ),
    "BB-TRN-05": (
        "Bramley Bank Staff Training Standard. All staff who handle customer "
        "accounts must complete compliance training before their first solo shift "
        "and refresher training every twelve months thereafter. Training completion "
        "must be recorded with the staff member's name, the course title, and the "
        "completion date. A manager must confirm that training is complete before "
        "assigning account-handling duties."
    ),
}

# Regression questions: (question, expected source_id that must be cited).
# These are regression checks on a tiny hand-written set (n=6), not quality
# claims about retrieval in general. See README for the honest framing.
REGRESSION_SET: list[tuple[str, str]] = [
    ("How long must identity verification records be kept after an account closes?",
     "BB-CDD-01"),
    ("How quickly must compliance records be retrievable after a request?",
     "BB-REC-02"),
    ("Within how many business days must staff raise an internal report about unusual activity?",
     "BB-AML-03"),
    ("How often must customer risk ratings be reviewed?",
     "BB-KYC-04"),
    ("How often must staff complete refresher compliance training?",
     "BB-TRN-05"),
    ("Must staff tell a customer that a suspicious activity report has been raised?",
     "BB-AML-03"),
]


def load_corpus() -> list[Chunk]:
    chunks: list[Chunk] = []
    for source_id, text in _DOCUMENTS.items():
        chunks.extend(chunk_text(text, source_id, max_chars=600, overlap=100))
    return chunks
