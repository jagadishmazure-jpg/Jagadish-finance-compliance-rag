# Built vs planned

## Built (code + green tests in this scaffold)

- Chunking with overlap and stable citation ids
- TF-IDF retrieval (stdlib) with a documented embedding swap point
- Question → cited answer, needs-review band, abstention + escalation
- Synthetic corpus (5 documents) + 6-question regression set
- View-aware SQLite authorizer + fetch-time row cap
- Confirmation gate + named-person, single-use, scoped, expiring approvals
- PII redaction (card numbers, email addresses, phone numbers, SSNs)
- Negative-cost rejection, email dry-run default, brand hash check
- Docs: README + this `docs/` set + `knowledge/`

## Written, not run

Nothing in this scaffold is in this category: every module listed as
Built is exercised by the 60-test suite, run green locally.

## Planned (not built, not claimed)

- Real embeddings and a vector store behind the swap point
- A real (licensed, counsel-reviewed) regulation corpus
- Durable escalation queue, reviewer UI, and audit log
- Evaluation harness beyond the 6-question regression set
- Deployment, packaging, hosted demo, badges, CI workflows
