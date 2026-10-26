"""Confirmation gate for publishing an answer to a human reviewer.

The gate refuses unless ALL of these hold:
- a pending approval exists (absent path: no approval -> refuse);
- the approval has not been bypassed (approve() without request -> error);
- the reviewer did not reject (reject() marks the request rejected);
- consent is exactly "yes" (low-confidence / hedged consent is refused);
- consent is not self-contradicting: any text containing both a "yes"
  and a "no" (e.g. "yes, wait, no") is refused, even if it starts with yes;
- the underlying approval is valid (named person, single-use, scoped,
  unexpired -- see approvals.py).

Consent is checked on the raw text the reviewer typed, lower-cased and
stripped; nothing is inferred from tone or partial matches.
"""

from __future__ import annotations

from compliance_rag.approvals import Approval, ApprovalError, request_approval


class GateError(Exception):
    pass


def _is_contradicting(consent: str) -> bool:
    lowered = consent.lower()
    has_yes = "yes" in lowered
    has_no = ("no" in lowered) or ("wait" in lowered) or ("stop" in lowered)
    return has_yes and has_no


class ConfirmationGate:
    def __init__(self, scope: str):
        self.scope = scope
        self._approval: Approval | None = None
        self._rejected = False

    def request(self, approver: str) -> None:
        self._approval = request_approval(approver, self.scope)
        self._rejected = False

    def reject(self) -> None:
        self._rejected = True

    def confirm(self, consent: str, confidence: float = 1.0,
                min_confidence: float = 0.5) -> bool:
        """Return True only if the gate passes; raise GateError otherwise."""
        if self._approval is None:
            raise GateError("no approval requested: gate refuses (absent path)")
        if self._rejected:
            raise GateError("reviewer rejected: gate refuses")
        if confidence < min_confidence:
            raise GateError(
                f"low confidence {confidence} below {min_confidence}: gate refuses")
        cleaned = (consent or "").strip().lower()
        if not cleaned:
            raise GateError("empty consent: gate refuses")
        if _is_contradicting(cleaned):
            raise GateError(
                "self-contradicting consent (contains both yes and no/wait): "
                "gate refuses")
        if cleaned != "yes":
            raise GateError(f"consent {consent!r} is not an explicit 'yes'")
        try:
            self._approval.consume(self.scope)
        except ApprovalError as exc:
            raise GateError(str(exc)) from exc
        return True
