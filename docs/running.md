# How to run (offline first)

Requirements: Python 3.11+ and pytest. Standard library only — there is
nothing to install.

```bash
python3 -m pytest tests/ -q   # 60 tests
python3 scripts/run_demo.py   # cited answer + refusal + regression table
python3 scripts/brand_check.py .
```

Optional checks that need an external file (not committed to the repo):

```bash
# 8-word overlap check of all repo docs against a source text file:
python3 scripts/overlap_check.py /path/to/source-text.txt
```

There is no server, no database file, no network call, and no
credential anywhere in the flow. The SQLite store is in-memory.
Cloud deployment is deliberately not provided in this scaffold.
