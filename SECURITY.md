# Security policy

## Scope

This is a learning scaffold with synthetic data only. It is not a
compliance product and must not be used to answer real regulatory
questions.

## Reporting

If you find a security issue in this scaffold (for example, an
authorizer bypass, a gate that can be circumvented, or PII leaking
through redaction), please report it via the repository's private
vulnerability reporting channel. Do not post exploit details publicly.

## What is enforced here

- SQLite access is view-only, enforced by the database authorizer
  (see `docs/guardrails.md`).
- Publication requires a named-person, single-use, scoped, unexpired
  approval plus an explicit "yes".
- PII (card numbers, email addresses, phone numbers, SSNs) is redacted
  before display or logging.
- Email is dry-run by default and refused in CI; no credentials are
  stored in this repo.

## Known open items

No audit log, no real reviewer identity (SSO), and no durable
escalation queue — all listed as Planned in `docs/built-vs-planned.md`.
