# Guardrails and security controls

Every control below has a named proof test. If the README says a thing
is enforced, a test proves it — otherwise the claim is removed.

| Control | Implementation | Proof test |
|---|---|---|
| Base-table reads denied | SQLite authorizer, view-name check on both authorizer args | `test_base_table_read_denied`, `test_base_table_read_denied_even_when_view_named_in_text` |
| `sqlite_master` denied | Authorizer denies non-view reads | `test_sqlite_master_read_denied` |
| Writes denied | Authorizer denies INSERT/UPDATE/DELETE | `test_write_denied`, `test_update_and_delete_denied` |
| PRAGMA / ATTACH / load_extension denied | Authorizer denies those actions | `test_pragma_denied`, `test_attach_denied` |
| Join with a base table denied | Authorizer sees the base-table read event | `test_join_with_base_table_denied` |
| Gate bypass refused | No approval → `GateError` | `test_gate_absent_path_refuses`, `test_gate_bypass_refuses_without_request` |
| Gate reject refused | `reject()` blocks `confirm()` | `test_gate_reject_path_refuses` |
| Low-confidence consent refused | Confidence below minimum → `GateError` | `test_gate_low_confidence_refused` |
| Contradicting consent refused | "yes, wait, no" and variants → `GateError` | `test_gate_contradicting_consent_refused`, `test_gate_contradicting_consent_variants_refused` |
| Approvals named-person, single-use, scoped, expiring | `compliance_rag/approvals.py` | `test_approval_requires_named_person`, `test_approval_single_use`, `test_approval_scope_mismatch_refused`, `test_approval_expired_refused`, `test_gate_second_confirm_fails_single_use` |
| PII redaction: cards + emails + phone + SSN | `compliance_rag/redaction.py` | `test_redaction_removes_card_number`, `test_redaction_removes_dashed_card_number`, `test_redaction_removes_email_address`, `test_redaction_removes_phone_and_ssn` |
| Row cap at fetch time | `fetchmany(MAX + 1)`, raise on overflow | `test_row_cap_enforced_via_fetchmany`, `test_row_cap_allows_within_cap` |
| Negative costs rejected | `validate_cost` raises, never clamps | `test_negative_cost_rejected`, `test_negative_budget_rejected`, `test_negative_add_rejected_and_total_unchanged` |
| Brand blocklist non-empty | Hashes only, asserted in a test | `test_brand_blocklist_non_empty` |
| Email dry-run default, refused in CI | `send_email(send=False)` default; CI env refuses opt-in | `test_email_dry_run_by_default`, `test_email_refused_in_ci_even_with_opt_in` |
| Abstention on weak retrieval | No claims, escalation flag | `test_abstention_on_weak_retrieval_gives_no_claims`, `test_abstention_on_empty_question`, `test_abstention_on_no_passage_retrieved` |

Authorizer subtlety, documented so it is not "fixed" away: a read
through a view fires two authorizer events — one for the underlying
base table tagged with the view name, and one for the view itself. The
authorizer allows a read only when one of those two names is an allowed
view. A direct base-table read has neither, so it is denied. Tests
execute real queries; no test in this repo inspects SQL text to decide
pass/fail.
