"""Confirmation gates, approvals, PII redaction, budget, brand, email."""

import os

import pytest

from compliance_rag.approvals import ApprovalError, request_approval
from compliance_rag.brand import BLOCKLIST_HASHES, find_blocked
from compliance_rag.budget import BudgetError, CostTracker, validate_cost
from compliance_rag.email_channel import EmailRefused, send_email
from compliance_rag.gates import ConfirmationGate, GateError
from compliance_rag.redaction import redact


# --- Confirmation gate: bypass / reject / absent / low-confidence /
#     self-contradicting consent ---

def _gate():
    gate = ConfirmationGate("publish-answer")
    gate.request("Priya Nair")
    return gate


def test_gate_passes_on_explicit_yes():
    assert _gate().confirm("yes") is True


def test_gate_absent_path_refuses():
    gate = ConfirmationGate("publish-answer")
    with pytest.raises(GateError):
        gate.confirm("yes")


def test_gate_reject_path_refuses():
    gate = _gate()
    gate.reject()
    with pytest.raises(GateError):
        gate.confirm("yes")


def test_gate_bypass_refuses_without_request():
    """Approving without a prior request is a bypass attempt: refused."""
    gate = ConfirmationGate("publish-answer")
    with pytest.raises(GateError):
        gate.confirm("yes")


def test_gate_non_yes_consent_refused():
    with pytest.raises(GateError):
        _gate().confirm("maybe")


def test_gate_low_confidence_refused():
    with pytest.raises(GateError):
        _gate().confirm("yes", confidence=0.2, min_confidence=0.5)


def test_gate_contradicting_consent_refused():
    """PROOF: 'yes, wait, no' is self-contradicting and must be refused."""
    with pytest.raises(GateError):
        _gate().confirm("yes, wait, no")


def test_gate_contradicting_consent_variants_refused():
    for consent in ("yes but no", "yes, stop", "yes no"):
        with pytest.raises(GateError):
            _gate().confirm(consent)


# --- Approvals: named-person, single-use, scoped, expiring ---

def test_approval_requires_named_person():
    with pytest.raises(ApprovalError):
        request_approval("", "publish-answer")


def test_approval_single_use():
    approval = request_approval("Priya Nair", "publish-answer")
    approval.consume("publish-answer")
    with pytest.raises(ApprovalError):
        approval.consume("publish-answer")


def test_approval_scope_mismatch_refused():
    approval = request_approval("Priya Nair", "publish-answer")
    with pytest.raises(ApprovalError):
        approval.consume("delete-records")


def test_approval_expired_refused():
    from datetime import datetime, timedelta, timezone
    approval = request_approval("Priya Nair", "publish-answer", ttl_minutes=30)
    approval.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    with pytest.raises(ApprovalError):
        approval.consume("publish-answer")


def test_gate_second_confirm_fails_single_use():
    gate = _gate()
    assert gate.confirm("yes") is True
    with pytest.raises(GateError):
        gate.confirm("yes")


# --- PII redaction: cards + emails, plus phone + SSN ---

def test_redaction_removes_card_number():
    out = redact("card 4111 1111 1111 1111 was used")
    assert "4111" not in out
    assert "[REDACTED-CARD]" in out


def test_redaction_removes_dashed_card_number():
    out = redact("card 4111-1111-1111-1111 was used")
    assert "4111" not in out


def test_redaction_removes_email_address():
    out = redact("contact jane.doe@example.com for details")
    assert "jane.doe@example.com" not in out
    assert "[REDACTED-EMAIL]" in out


def test_redaction_removes_phone_and_ssn():
    out = redact("call 555-123-4567, SSN 123-45-6789")
    assert "555-123-4567" not in out
    assert "123-45-6789" not in out
    assert "[REDACTED-PHONE]" in out
    assert "[REDACTED-SSN]" in out


def test_redaction_leaves_clean_text_untouched():
    assert redact("retention period is seven years") == "retention period is seven years"


# --- Budget: negatives rejected ---

def test_negative_cost_rejected():
    with pytest.raises(BudgetError):
        validate_cost(-1.0)
    with pytest.raises(BudgetError):
        validate_cost(-0.01)


def test_negative_budget_rejected():
    with pytest.raises(BudgetError):
        CostTracker(-5.0)


def test_negative_add_rejected_and_total_unchanged():
    tracker = CostTracker(10.0)
    tracker.add(2.0)
    with pytest.raises(BudgetError):
        tracker.add(-2.0)
    assert tracker.spent == 2.0


def test_zero_cost_allowed_and_over_budget_detected():
    tracker = CostTracker(1.0)
    assert tracker.add(0.0) == 0.0
    tracker.add(2.0)
    assert tracker.over_budget() is True


# --- Brand blocklist: non-empty ---

def test_brand_blocklist_non_empty():
    assert len(BLOCKLIST_HASHES) > 0
    assert all(len(h) == 64 and all(c in "0123456789abcdef" for c in h)
               for h in BLOCKLIST_HASHES)


def test_brand_check_finds_nothing_in_clean_text():
    assert find_blocked("Bramley Bank compliance answer") == []


# --- Email channel: dry-run default, refused in CI ---

def test_email_dry_run_by_default():
    record = send_email("reviewer@example.com", "Review needed", "draft")
    assert record.sent is False
    assert record.dry_run is True


def test_email_refused_in_ci_even_with_opt_in(monkeypatch):
    monkeypatch.setenv("CI", "true")
    with pytest.raises(EmailRefused):
        send_email("reviewer@example.com", "Review needed", "draft", send=True)


def test_email_opt_in_outside_ci_does_not_transmit(monkeypatch):
    monkeypatch.delenv("CI", raising=False)
    record = send_email("reviewer@example.com", "Review needed", "draft", send=True)
    # No transport is configured in this scaffold, so nothing is sent.
    assert record.sent is False
