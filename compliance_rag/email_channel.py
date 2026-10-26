"""Email channel: dry_run=True by default, explicit opt-in to send.

- Default behaviour is a dry run: nothing is sent, a record is returned.
- Sending requires an explicit ``send=True`` argument at the call site.
- In CI (CI env var set) sending is REFUSED outright, even with opt-in.
- No credentials live in this repo; the channel never reads a password,
  token, or key. A real send would be wired by the adopter, not here.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


class EmailRefused(Exception):
    pass


@dataclass
class EmailRecord:
    to: str
    subject: str
    body: str
    sent: bool
    dry_run: bool


def send_email(to: str, subject: str, body: str, send: bool = False) -> EmailRecord:
    if not send:
        return EmailRecord(to=to, subject=subject, body=body,
                           sent=False, dry_run=True)
    if os.environ.get("CI"):
        raise EmailRefused("email sending is refused in CI")
    # Explicit opt-in outside CI: this scaffold still does not transmit,
    # because no mail transport or credential is configured. The record
    # marks the intent so an adopter can wire a transport behind this point.
    return EmailRecord(to=to, subject=subject, body=body,
                       sent=False, dry_run=False)
