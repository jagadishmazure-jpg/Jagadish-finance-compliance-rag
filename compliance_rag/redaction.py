"""PII redaction for logs and displayed answers.

Checklist (all tested, not just phone/SSN):
- CARD NUMBERS: 13-19 digits, optionally spaced or dashed;
- EMAIL ADDRESSES;
- phone numbers;
- SSNs (XXX-XX-XXXX).

Redaction replaces the matched value with a labelled placeholder so a
reviewer can see that something was removed, without seeing the value.
"""

from __future__ import annotations

import re

_CARD = re.compile(r"\b(?:\d[ -]?){12,18}\d\b")
_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_PHONE = re.compile(r"\b(?:\+?1[-. ]?)?(?:\(?\d{3}\)?[-. ]?)\d{3}[-. ]?\d{4}\b")
_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def redact(text: str) -> str:
    if not text:
        return text
    # Order matters: SSN and email first so their digits are not eaten by
    # the card/phone patterns, then card, then phone.
    text = _SSN.sub("[REDACTED-SSN]", text)
    text = _EMAIL.sub("[REDACTED-EMAIL]", text)
    text = _CARD.sub("[REDACTED-CARD]", text)
    text = _PHONE.sub("[REDACTED-PHONE]", text)
    return text
