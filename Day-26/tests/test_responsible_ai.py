"""Comprehensive PyTest suite for Day 26 Responsible AI Guardrails POC."""

import os
import json
import pytest
from app.models import PIITypeEnum, PrivacyScrubResult, FairnessMetrics, GroundingVerificationResult
from app.guardrails.privacy_masker import PrivacyMasker
from app.guardrails.fairness_auditor import FairnessAuditor
from app.guardrails.grounding_verifier import GroundingVerifier
from app.guardrails.pipeline import ResponsibleAIPipeline


# ------------------------------------------------------------------------------------
# 1. Privacy Masker Unit Tests
# ------------------------------------------------------------------------------------
def test_email_redaction():
    text = "Contact john.doe@linkific.in for details."
    res = PrivacyMasker.scrub_text(text)
    assert res.redacted_count == 1
    assert "[EMAIL_01]" in res.sanitized_text
    assert "john.doe@linkific.in" not in res.sanitized_text


def test_credit_card_redaction():
    text = "Charged to 4111-2222-3333-4444 on file."
    res = PrivacyMasker.scrub_text(text)
    assert res.redacted_count == 1
    assert "[CREDIT_CARD_01]" in res.sanitized_text
    assert "4111-2222-3333-4444" not in res.sanitized_text


def test_indian_pan_card_redaction():
    text = "Vendor PAN is ABCDE1234F verified."
    res = PrivacyMasker.scrub_text(text)
    assert res.redacted_count == 1
    assert "[PAN_01]" in res.sanitized_text
    assert "ABCDE1234F" not in res.sanitized_text


def test_indian_aadhaar_redaction():
    text = "UIDAI number is 4123 8812 9904 registered."
    res = PrivacyMasker.scrub_text(text)
    assert res.redacted_count == 1
    assert "[AADHAAR_01]" in res.sanitized_text


def test_bank_account_redaction():
    text = "Disbursement Account: 91823746192837 at SBI."
    res = PrivacyMasker.scrub_text(text)
    assert res.redacted_count >= 1
    assert "[ACCOUNT_NUMBER_01]" in res.sanitized_text
    assert "91823746192837" not in res.sanitized_text


def test_empty_privacy_text():
    res = PrivacyMasker.scrub_text("")
    assert res.redacted_count == 0
    assert res.sanitized_text == ""


def test_reversible_rehydration():
    orig = "Send invoice to dev@linkific.in with PAN ABCDE1234F."
    scrubbed = PrivacyMasker.scrub_text(orig)
    rehydrated = PrivacyMasker.rehydrate_text(scrubbed.sanitized_text, scrubbed.surrogate_map)
    assert rehydrated == orig


# ------------------------------------------------------------------------------------
# 2. Fairness Auditor & Disparate Impact Unit Tests
# ------------------------------------------------------------------------------------
def test_fairness_four_fifths_pass():
    # Group A: 50 approved out of 100 (50%)
    # Group B: 45 approved out of 100 (45%)
    # DIR = 45 / 50 = 0.90 (>= 0.80) -> PASS
    records = [{"grp": "A", "approved": True}] * 50 + [{"grp": "A", "approved": False}] * 50
    records += [{"grp": "B", "approved": True}] * 45 + [{"grp": "B", "approved": False}] * 55

    metrics = FairnessAuditor.audit_decisions(
        records=records,
        protected_attribute="grp",
        privileged_group_value="A",
        unprivileged_group_value="B",
    )
    assert metrics.passes_four_fifths_rule is True
    assert metrics.disparate_impact_ratio == 0.90
    assert metrics.status == "COMPLIANT"


def test_fairness_four_fifths_violation():
    # Group A: 80 approved out of 100 (80%)
    # Group B: 20 approved out of 100 (20%)
    # DIR = 20 / 80 = 0.25 (< 0.80) -> FAIL
    records = [{"grp": "A", "approved": True}] * 80 + [{"grp": "A", "approved": False}] * 20
    records += [{"grp": "B", "approved": True}] * 20 + [{"grp": "B", "approved": False}] * 80

    metrics = FairnessAuditor.audit_decisions(
        records=records,
        protected_attribute="grp",
        privileged_group_value="A",
        unprivileged_group_value="B",
    )
    assert metrics.passes_four_fifths_rule is False
    assert metrics.disparate_impact_ratio == 0.25
    assert metrics.status == "NON_COMPLIANT_BIASED"
    assert len(metrics.violations) > 0


def test_fairness_empty_records():
    metrics = FairnessAuditor.audit_decisions([], "region")
    assert metrics.total_evaluated == 0
    assert metrics.status == "NO_DATA"


def test_biased_dataset_file():
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "biased_decision_log.json")
    assert os.path.exists(data_path)
    with open(data_path, "r") as f:
        data = json.load(f)
    metrics = FairnessAuditor.audit_decisions(
        records=data,
        protected_attribute="region",
        privileged_group_value="Metro",
        unprivileged_group_value="Rural",
    )
    assert metrics.passes_four_fifths_rule is False
    assert metrics.disparate_impact_ratio == 0.25


def test_fair_dataset_file():
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "fair_decision_log.json")
    assert os.path.exists(data_path)
    with open(data_path, "r") as f:
        data = json.load(f)
    metrics = FairnessAuditor.audit_decisions(
        records=data,
        protected_attribute="region",
        privileged_group_value="Metro",
        unprivileged_group_value="Rural",
    )
    assert metrics.passes_four_fifths_rule is True
    assert metrics.disparate_impact_ratio == 1.0


# ------------------------------------------------------------------------------------
# 3. Grounding Verifier & Hallucination Unit Tests
# ------------------------------------------------------------------------------------
def test_grounded_response_passes():
    src = "PO-100: Total is $500.00 USD for 10 monitors."
    gen = "Purchase order PO-100 total is $500.00 USD for 10 monitors."
    res = GroundingVerifier.verify_grounding(gen, src)
    assert res.is_grounded is True
    assert res.action == "ALLOW"
    assert len(res.numerical_discrepancies) == 0


def test_altered_number_hallucination_blocked():
    src = "PO-100: Total is $500.00 USD."
    gen = "PO-100: Total is $580.00 USD."  # altered amount!
    res = GroundingVerifier.verify_grounding(gen, src)
    assert res.is_grounded is False
    assert res.action == "BLOCK_HALLUCINATION"
    assert any(d["hallucinated_number"] == "580.00" for d in res.numerical_discrepancies)


def test_invented_discount_number_blocked():
    src = "Invoice INV-90: Amount due $1,200.00."
    gen = "Invoice INV-90: Amount due $1,200.00 after $300.00 discount."
    res = GroundingVerifier.verify_grounding(gen, src)
    assert res.is_grounded is False
    assert res.action == "BLOCK_HALLUCINATION"
    assert any(d["hallucinated_number"] == "300.00" for d in res.numerical_discrepancies)


def test_empty_generation_grounding():
    res = GroundingVerifier.verify_grounding("", "Some source context")
    assert res.is_grounded is True
    assert res.action == "ALLOW"


# ------------------------------------------------------------------------------------
# 4. End-to-End Pipeline Integration Tests
# ------------------------------------------------------------------------------------
def test_full_pipeline_approval():
    pipeline = ResponsibleAIPipeline()
    raw_prompt = "User Amit (amit@linkific.in) approving INV-10."
    src = "INVOICE #INV-10: Total payable USD $1,000.00 to Dell Inc."
    llm_out = "Invoice #INV-10 total payable USD $1,000.00 to Dell Inc is confirmed."

    fair_data = [{"region": "Metro", "approved": True}, {"region": "Rural", "approved": True}]

    res = pipeline.run_full_guardrail_cycle(
        user_input_with_pii=raw_prompt,
        simulated_llm_output=llm_out,
        reference_source_doc=src,
        historical_decisions=fair_data,
        protected_col="region",
        privileged_group="Metro",
        unprivileged_group="Rural",
    )
    assert res["audit_record"].overall_compliance_decision == "APPROVED"
    assert res["privacy_result"].redacted_count == 1
    assert res["grounding_result"].is_grounded is True


def test_full_pipeline_rejection_on_hallucination():
    pipeline = ResponsibleAIPipeline()
    raw_prompt = "User Amit approving INV-10."
    src = "INVOICE #INV-10: Total payable USD $1,000.00."
    hallucinated_out = "Invoice #INV-10 payable USD $1,850.00."  # Bad amount

    res = pipeline.run_full_guardrail_cycle(
        user_input_with_pii=raw_prompt,
        simulated_llm_output=hallucinated_out,
        reference_source_doc=src,
        historical_decisions=[],
    )
    assert res["audit_record"].overall_compliance_decision == "REJECTED_ETHICS_VIOLATION"
    assert res["grounding_result"].is_grounded is False
