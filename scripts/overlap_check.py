"""8-word overlap check: repo docs vs an external source text.

Usage: python3 scripts/overlap_check.py <source-text-file> [docs-dir ...]
Exits non-zero and prints every shared 8-word sequence found. Target: 0.
The source text file is NOT committed to the repo; pass it as an argument.
Comparison is case-insensitive, punctuation-normalised, word-sequence based.
"""

import re
import sys
from pathlib import Path

_WORD = re.compile(r"[a-z0-9]+")


def sequences(text: str, n: int = 8) -> set[tuple[str, ...]]:
    words = _WORD.findall(text.lower())
    return {tuple(words[i:i + n]) for i in range(len(words) - n + 1)}


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: overlap_check.py <source-text-file> [docs-dir ...]")
        return 2
    source = sequences(Path(sys.argv[1]).read_text(errors="ignore"))
    roots = [Path(p) for p in sys.argv[2:]] or [Path("README.md"), Path("docs"),
                                                Path("knowledge")]
    hits: set[tuple[str, ...]] = set()
    for root in roots:
        files = [root] if root.is_file() else sorted(root.rglob("*.md"))
        for f in files:
            hits |= sequences(f.read_text(errors="ignore")) & source
    for hit in sorted(hits):
        print("OVERLAP:", " ".join(hit))
    print(f"8-word overlap hits: {len(hits)}")
    return 1 if hits else 0


if __name__ == "__main__":
    raise SystemExit(main())
