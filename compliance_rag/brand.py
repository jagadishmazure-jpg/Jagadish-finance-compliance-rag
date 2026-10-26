"""Brand/name check: blocklist stored as SHA-256 hashes, never plain names.

The check hashes each token of a document and reports any token whose
hash is in the blocklist. The source strings behind the hashes are
intentionally NOT stored in this repo. A test asserts the blocklist is
non-empty and that every entry is a 64-character hex digest.
"""

from __future__ import annotations

import hashlib
import re

# SHA-256 hashes of disallowed brand strings (hashes only).
BLOCKLIST_HASHES: tuple[str, ...] = (
    "3b8eccd79c406969d8fa1a98deea4b0a3d13df5959d6ea421b99222a64055246",
    "7105a46cb4c2810f0c916e0bb4b4e4ef834ad42040c471b42c96d356a9fd1b21",
    "4ef9bfe6a5402861fd19b51cdbe76e50ac1cd3cf36e3d20530d57f5dd13ab60e",
    "ce749e840dcada0f9196edd49327ae5b3ab16f1d0405e72c1cb7d62b04538a42",
    "71f566aba763fb7636f03bfeb321c6d4934d4a6d5cb777c49b1c1595260c573b",
)

_TOKEN = re.compile(r"[a-z0-9]+")


def find_blocked(text: str) -> list[str]:
    """Return the hashes of any blocked token found in ``text``."""
    found: list[str] = []
    for token in _TOKEN.findall(text.lower()):
        digest = hashlib.sha256(token.encode()).hexdigest()
        if digest in BLOCKLIST_HASHES and digest not in found:
            found.append(digest)
    return found
