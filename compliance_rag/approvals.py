"""Named-person, single-use, scoped, expiring approvals.

An approval is valid only when ALL of these hold:
- it names a real approver (non-empty person name, not a role label);
- it has not been consumed before (single-use);
- the action being performed matches the approved scope exactly;
- it has not expired.
Any failure raises; there is no silent fallback to "approved".
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone


class ApprovalError(Exception):
    pass


@dataclass
class Approval:
    approver: str
    scope: str
    expires_at: datetime
    consumed: bool = False

    def consume(self, action: str, now: datetime | None = None) -> None:
        now = now or datetime.now(timezone.utc)
        if not self.approver or not self.approver.strip():
            raise ApprovalError("approval has no named approver")
        if self.consumed:
            raise ApprovalError("approval is single-use and already consumed")
        if action != self.scope:
            raise ApprovalError(
                f"approval scope {self.scope!r} does not cover action {action!r}")
        if now >= self.expires_at:
            raise ApprovalError("approval has expired")
        self.consumed = True


def request_approval(approver: str, scope: str,
                     ttl_minutes: int = 30) -> Approval:
    if not approver or not approver.strip():
        raise ApprovalError("approver must be a named person")
    if ttl_minutes <= 0:
        raise ApprovalError("approval TTL must be positive")
    return Approval(approver=approver.strip(), scope=scope,
                    expires_at=datetime.now(timezone.utc)
                    + timedelta(minutes=ttl_minutes))
