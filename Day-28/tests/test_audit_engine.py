"""Unit & Integration Tests for FinDoc-AuditEngine Core Services.

Validates:
1. 3-Way Reconciliation matching engine (PO, Invoice, Dock Receipt)
2. Isolation Forest ML Risk Scorer & Explainable Feature Contributions
3. Corporate Governance Approval Router & Dual Currency USD/INR Math
4. Responsible AI PII Privacy Scrubber
"""

import pytest
from app.core.config import settings
from app.core.privacy import FinancialPrivacyScrubber
from app.models import (
    ApprovalTierEnum,
    InvoicePayload,
    LineItem,
    PurchaseOrderRecord,
    RiskLevelEnum,
)
from app.services.anomaly_detector import AnomalyScorer
from app.services.matcher import ReconciliationMatcher
from app.services.router import ApprovalRouter


# --------------------------------------------------------------------------
# 1. 3-Way Reconciliation Tests
# --------------------------------------------------------------------------

def test_reconciliation_exact_match():
    """Verify that identical invoice and PO with 100% accepted dock receipts pass match cleanly."""
    item = LineItem(item_id="ITEM-A", description="Server Rack", unit_price_usd=500.0, quantity=2)
    invoice = InvoicePayload(
        invoice_id="INV-TEST-01",
        vendor_name="ServerCorp",
        total_amount_usd=1000.0,
        po_number="PO-TEST-01",
        items=[item],
    )
    po = PurchaseOrderRecord(
        po_number="PO-TEST-01",
        vendor_name="ServerCorp",
        total_amount_usd=1000.0,
        items=[item],
        grn_units_received={"ITEM-A": 2},
        grn_units_rejected={"ITEM-A": 0},
    )

    result = ReconciliationMatcher.match(invoice, po)
    assert result.matched is True
    assert result.po_found is True
    assert result.price_variance_usd == 0.0
    assert result.quantity_variance_units == 0
    assert len(result.discrepancy_details) == 0


def test_reconciliation_price_variance():
    """Verify that vendor unit price markup over approved PO is detected and flagged."""
    inv_item = LineItem(item_id="ITEM-B", description="RAM Module", unit_price_usd=120.0, quantity=10)
    po_item = LineItem(item_id="ITEM-B", description="RAM Module", unit_price_usd=100.0, quantity=10)

    invoice = InvoicePayload(
        invoice_id="INV-TEST-02",
        vendor_name="MemoryDepot",
        total_amount_usd=1200.0,
        po_number="PO-TEST-02",
        items=[inv_item],
    )
    po = PurchaseOrderRecord(
        po_number="PO-TEST-02",
        vendor_name="MemoryDepot",
        total_amount_usd=1000.0,
        items=[po_item],
        grn_units_received={"ITEM-B": 10},
        grn_units_rejected={"ITEM-B": 0},
    )

    result = ReconciliationMatcher.match(invoice, po)
    assert result.matched is False
    assert result.price_variance_usd == 200.0  # ($120 - $100) * 10
    assert any("Rate Variance on item 'ITEM-B'" in d for d in result.discrepancy_details)


def test_reconciliation_dock_shortage_rejected_goods():
    """Verify that dock damage/rejected units result in quantity variance."""
    item = LineItem(item_id="ITEM-C", description="Monitors", unit_price_usd=200.0, quantity=5)
    invoice = InvoicePayload(
        invoice_id="INV-TEST-03",
        vendor_name="DisplayTech",
        total_amount_usd=1000.0,
        po_number="PO-TEST-03",
        items=[item],
    )
    po = PurchaseOrderRecord(
        po_number="PO-TEST-03",
        vendor_name="DisplayTech",
        total_amount_usd=1000.0,
        items=[item],
        grn_units_received={"ITEM-C": 5},
        grn_units_rejected={"ITEM-C": 2},  # 2 units damaged at dock
    )

    result = ReconciliationMatcher.match(invoice, po)
    assert result.matched is False
    assert result.quantity_variance_units == 2
    assert any("Quantity Discrepancy" in d for d in result.discrepancy_details)


def test_reconciliation_missing_po():
    """Verify that invoice referencing a non-existent PO fails matching with explicit flag."""
    item = LineItem(item_id="ITEM-D", description="Office Supplies", unit_price_usd=50.0, quantity=2)
    invoice = InvoicePayload(
        invoice_id="INV-TEST-04",
        vendor_name="UnknownCorp",
        total_amount_usd=100.0,
        po_number="PO-NONEXISTENT",
        items=[item],
    )

    result = ReconciliationMatcher.match(invoice, None)
    assert result.matched is False
    assert result.po_found is False
    assert any("not found" in d for d in result.discrepancy_details)


# --------------------------------------------------------------------------
# 2. ML Risk Engine & Feature Contributions
# --------------------------------------------------------------------------

def test_anomaly_scorer_bounds_and_contributions():
    """Verify that ML anomaly scores are bounded [0, 100] and return explainability vectors."""
    scorer = AnomalyScorer()
    item = LineItem(item_id="ITEM-E", description="Standard Supplies", unit_price_usd=20.0, quantity=10)
    invoice = InvoicePayload(
        invoice_id="INV-TEST-05",
        vendor_name="CleanVendor",
        total_amount_usd=200.0,
        vendor_country="IN",
        is_new_vendor=False,
        items=[item],
    )
    match_result = ReconciliationMatcher.match(invoice, None)

    risk = scorer.assess_risk(invoice, match_result)
    assert 0.0 <= risk.anomaly_score <= 100.0
    assert isinstance(risk.risk_level, RiskLevelEnum)
    assert len(risk.feature_contributions) == 5
    for feat in risk.feature_contributions:
        assert feat.feature_name != ""
        assert feat.risk_contribution >= 0.0


def test_anomaly_scorer_offshore_tax_haven_flags():
    """Verify that offshore tax havens (e.g. Belize 'BZ') elevate risk to CRITICAL."""
    scorer = AnomalyScorer()
    item = LineItem(item_id="ITEM-F", description="Consulting Fee", unit_price_usd=45000.0, quantity=1)
    invoice = InvoicePayload(
        invoice_id="INV-TEST-06",
        vendor_name="Offshore Shell Entity",
        total_amount_usd=45000.0,
        vendor_country="BZ",
        is_new_vendor=True,
        items=[item],
    )
    match_result = ReconciliationMatcher.match(invoice, None)

    risk = scorer.assess_risk(invoice, match_result)
    assert risk.risk_level == RiskLevelEnum.CRITICAL
    assert risk.anomaly_score >= 85.0
    assert any("BZ" in f for f in risk.risk_factors)


# --------------------------------------------------------------------------
# 3. Corporate Governance Approval Router & Dual Currency Math
# --------------------------------------------------------------------------

def test_governance_router_stp_tier():
    """Verify that low-risk invoices below $1,000 are routed to TIER_1_STP_AUTO_APPROVED."""
    scorer = AnomalyScorer()
    item = LineItem(item_id="ITEM-G", description="Printer Paper", unit_price_usd=50.0, quantity=5)
    invoice = InvoicePayload(
        invoice_id="INV-TEST-07",
        vendor_name="PaperSupply Ltd",
        total_amount_usd=250.0,
        po_number="PO-TEST-07",
        items=[item],
    )
    po = PurchaseOrderRecord(
        po_number="PO-TEST-07",
        vendor_name="PaperSupply Ltd",
        total_amount_usd=250.0,
        items=[item],
        grn_units_received={"ITEM-G": 5},
    )

    match_res = ReconciliationMatcher.match(invoice, po)
    risk = scorer.assess_risk(invoice, match_res)
    decision = ApprovalRouter.route_decision(invoice, match_res, risk, pii_count=0)

    assert decision.approval_tier == ApprovalTierEnum.TIER_1_STP
    assert decision.authorized is True
    assert decision.requires_hitl is False
    # Verify INR pegging @ 86.50
    assert decision.total_amount_inr == round(250.0 * 86.50, 2)


def test_governance_router_manager_review_tier():
    """Verify that invoices between $1,000 and $10,000 require Tier 2 Manager Review."""
    scorer = AnomalyScorer()
    item = LineItem(item_id="ITEM-H", description="Network Switch", unit_price_usd=3000.0, quantity=1)
    invoice = InvoicePayload(
        invoice_id="INV-TEST-08",
        vendor_name="Cisco Partner",
        total_amount_usd=3000.0,
        po_number="PO-TEST-08",
        items=[item],
    )
    po = PurchaseOrderRecord(
        po_number="PO-TEST-08",
        vendor_name="Cisco Partner",
        total_amount_usd=3000.0,
        items=[item],
        grn_units_received={"ITEM-H": 1},
    )

    match_res = ReconciliationMatcher.match(invoice, po)
    risk = scorer.assess_risk(invoice, match_res)
    decision = ApprovalRouter.route_decision(invoice, match_res, risk, pii_count=0)

    assert decision.approval_tier == ApprovalTierEnum.TIER_2_MANAGER
    assert decision.authorized is True
    assert decision.requires_hitl is True
    assert decision.total_amount_inr == round(3000.0 * 86.50, 2)


def test_governance_router_director_signoff_tier():
    """Verify that high-value disbursements (> $10,000) require Tier 3 Director Signoff."""
    scorer = AnomalyScorer()
    item = LineItem(item_id="ITEM-I", description="Datacenter Servers", unit_price_usd=25000.0, quantity=1)
    invoice = InvoicePayload(
        invoice_id="INV-TEST-09",
        vendor_name="Dell Enterprise",
        total_amount_usd=25000.0,
        po_number="PO-TEST-09",
        items=[item],
    )
    po = PurchaseOrderRecord(
        po_number="PO-TEST-09",
        vendor_name="Dell Enterprise",
        total_amount_usd=25000.0,
        items=[item],
        grn_units_received={"ITEM-I": 1},
    )

    match_res = ReconciliationMatcher.match(invoice, po)
    risk = scorer.assess_risk(invoice, match_res)
    decision = ApprovalRouter.route_decision(invoice, match_res, risk, pii_count=0)

    assert decision.approval_tier == ApprovalTierEnum.TIER_3_DIRECTOR
    assert decision.authorized is True
    assert decision.requires_hitl is True
    assert decision.total_amount_inr == round(25000.0 * 86.50, 2)


# --------------------------------------------------------------------------
# 4. Responsible AI Privacy Scrubber
# --------------------------------------------------------------------------

def test_privacy_scrubber_pan_aadhaar_phone_email():
    """Verify that PAN cards, Aadhaar numbers, phones, and emails are properly redacted."""
    raw_text = (
        "Vendor invoice contact: billing@acme.com, phone: +91 9876543210. "
        "Tax PAN: ABCDE1234F, Aadhaar ID: 1234 5678 9012, Bank: 987654321098."
    )
    scrubbed, count, redacts = FinancialPrivacyScrubber.scrub_text(raw_text)

    assert count >= 4
    assert "billing@acme.com" not in scrubbed
    assert "ABCDE1234F" not in scrubbed
    assert "1234 5678 9012" not in scrubbed
    assert "[EMAIL_" in scrubbed
    assert "[PAN_" in scrubbed
    assert "[AADHAAR_" in scrubbed

    # Also verify scrub_invoice helper
    inv = InvoicePayload(
        invoice_id="INV-PII-01",
        vendor_name="Test Corp",
        total_amount_usd=100.0,
        vendor_pan="ABCDE1234F",
        vendor_contact_email="test@corp.com",
        vendor_bank_account="123456789012",
    )
    scrubbed_inv, red_count = FinancialPrivacyScrubber.scrub_invoice(inv)
    assert red_count == 3
    assert scrubbed_inv.vendor_pan == "[REDACTED_PAN]"
    assert scrubbed_inv.vendor_contact_email == "[REDACTED_EMAIL]"
    assert scrubbed_inv.vendor_bank_account == "[REDACTED_ACCOUNT]"
