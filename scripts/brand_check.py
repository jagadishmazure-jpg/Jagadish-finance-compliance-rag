"""Brand check: scan repo markdown for tokens whose SHA-256 is blocklisted.

Usage: python3 scripts/brand_check.py [dir ...]
Exits non-zero if a blocked token hash is found. Blocklist lives in
compliance_rag/brand.py as hashes only, never plain names.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from compliance_rag.brand import find_blocked


def main() -> int:
    roots = [Path(p) for p in sys.argv[1:]] or [Path("README.md"), Path("docs"),
                                                Path("knowledge")]
    bad = 0
    for root in roots:
        files = [root] if root.is_file() else sorted(root.rglob("*.md"))
        for f in files:
            found = find_blocked(f.read_text(errors="ignore"))
            if found:
                print(f"BLOCKED token hash in {f}: {found}")
                bad += 1
    print(f"brand check: {'FAIL' if bad else 'PASS'} ({bad} files flagged)")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
