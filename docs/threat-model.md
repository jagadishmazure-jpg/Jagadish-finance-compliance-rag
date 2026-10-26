# Threat model and ADRs

## Threat model (STRIDE, scoped to this scaffold)

- **Spoofing:** a reviewer identity is just a name string in this
  scaffold. Mitigation: approvals require a non-empty named approver;
  real identity (SSO) is a Planned item, not claimed.
- **Tampering:** direct base-table access would let a caller read or
  alter passages outside the view contract. Mitigation: authorizer
  denies base tables, writes, PRAGMA, ATTACH, extension loading.
- **Repudiation:** without an audit log, a published answer cannot be
  traced to its approver. Status: open — audit log is Planned.
- **Information disclosure:** PII in questions or answers leaking into
  logs. Mitigation: redaction of cards, emails, phone, SSN before
  display/logging; tests per category.
- **Denial of service:** unbounded result sets. Mitigation: row cap via
  `fetchmany(MAX + 1)` at fetch time.
- **Elevation of privilege:** self-approval, reused approvals, or
  scope creep. Mitigation: named-person, single-use, scoped, expiring
  approvals; gate refuses bypass/reject/absent/low-confidence/
  contradicting consent.
- **LLM-specific (OWASP LLM Top 10, as applicable):** there is no model
  here, so prompt injection and model-output risks do not apply to this
  scaffold. The analogue risk — a confident answer with no supporting
  passage — is addressed structurally by abstention. If generation is
  added later, input/output guards and prompt-injection tests become
  mandatory before release.

## ADRs

### ADR-1: TF-IDF (stdlib) instead of embeddings
No dependency, no network, no API key; retrieval behaviour is fully
inspectable. Cost: lexical matching only. Reversible at the documented
swap point.

### ADR-2: Abstention by construction, not by instruction
Below threshold, no claims are built. This removes a whole class of
"the model answered anyway" failures, at the cost of refusing some
answerable-but-weakly-matching questions. That trade is correct for
compliance.

### ADR-3: Authorizer, not application code, enforces view-only access
A bug in query-building code cannot widen access, because the database
itself refuses. Cost: the two-event view subtlety must be understood
(see guardrails doc).

### ADR-4: Synthetic corpus, invented firm
Real regulation text and real firm names are deliberately absent, so
the scaffold can be public without legal or brand risk. Cost: no
real-world performance claim is possible.

### ADR-5: Claims are excerpts, not paraphrases
Verifiability over fluency. A reviewer checks an excerpt in seconds;
a paraphrase requires trusting the paraphraser.
