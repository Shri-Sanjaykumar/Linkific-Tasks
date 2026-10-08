"""Unit and Integration Tests for Linkific Enterprise FinDoc-AuditEngine (Day 27)."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import (
    InvoicePayload,
    PurchaseOrderRecord,
    LineItem,
    ApprovalTierEnum,
    RiskLevelEnum,
)
from app.services.matcher import ThreeWayMatcher
from app.services.anomaly_detector import AnomalyScorer
from app.services.router import ApprovalRouter
from app.core.privacy import PIIScrubber
from app.core.config import settings

client = TestClient(app)


# =====================================================================
# 1. Deterministic 3-Way Reconciliation Tests
# =====================================================================

def test_three_way_matcher_clean_match():
    """Verify clean 3-way match across invoice, PO, and warehouse GRN."""
    item = LineItem(item_id="ITM-1", description="Monitors", quantity=5, unit_price_usd=200.0, total_price_usd=1000.0)
    invoice = InvoicePayload(
        invoice_id="INV-TEST-01",
        vendor_id="V-1",
        vendor_name="TechSupplies Inc",
        po_number="PO-100",
        invoice_date="2026-10-01",
        due_date="2026-10-31",
        subtotal_usd=1000.0,
        tax_usd=0.0,
        total_amount_usd=1000.0,
        currency="USD",
        items=[item],
    )
    po = PurchaseOrderRecord(
        po_number="PO-100",
        vendor_id="V-1",
        approved_total_usd=1000.0,
        items=[item],
        grn_units_received={"ITM-1": 5},
        grn_units_rejected={"ITM-1": 0},
    )

    res = ThreeWayMatcher.reconcile(invoice, po)
    assert res.matched is True
    assert res.po_found is True
    assert res.price_variance_usd == 0.0
    assert res.quantity_variance_units == 0
    assert len(res.discrepancy_details) == 0


def test_three_way_matcher_price_variance():
    """Verify detection of price inflation above PO baseline."""
    inv_item = LineItem(item_id="ITM-1", description="Monitors", quantity=5, unit_price_usd=250.0, total_price_usd=1250.0)
    po_item = LineItem(item_id="ITM-1", description="Monitors", quantity=5, unit_price_usd=200.0, total_price_usd=1000.0)
    invoice = InvoicePayload(
        invoice_id="INV-TEST-02",
        vendor_id="V-1",
        vendor_name="TechSupplies Inc",
        po_number="PO-100",
        invoice_date="2026-10-01",
        due_date="2026-10-31",
        subtotal_usd=1250.0,
        tax_usd=0.0,
        total_amount_usd=1250.0,
        currency="USD",
        items=[inv_item],
    )
    po = PurchaseOrderRecord(
        po_number="PO-100",
        vendor_id="V-1",
        approved_total_usd=1000.0,
        items=[po_item],
        grn_units_received={"ITM-1": 5},
    )

    res = ThreeWayMatcher.reconcile(invoice, po)
    assert res.matched is False
    assert res.price_variance_usd == 250.0
    assert any("Rate Variance" in d for d in res.discrepancy_details)


def test_three_way_matcher_quantity_shortage():
    """Verify dock GRN shortage detection."""
    item = LineItem(item_id="ITM-1", description="Monitors", quantity=10, unit_price_usd=100.0, total_price_usd=1000.0)
    invoice = InvoicePayload(
        invoice_id="INV-TEST-03",
        vendor_id="V-1",
        vendor_name="TechSupplies Inc",
        po_number="PO-100",
        invoice_date="2026-10-01",
        due_date="2026-10-31",
        subtotal_usd=1000.0,
        tax_usd=0.0,
        total_amount_usd=1000.0,
        currency="USD",
        items=[item],
    )
    po = PurchaseOrderRecord(
        po_number="PO-100",
        vendor_id="V-1",
        approved_total_usd=1000.0,
        items=[item],
        grn_units_received={"ITM-1": 7},  # 3 missing!
    )

    res = ThreeWayMatcher.reconcile(invoice, po)
    assert res.matched is False
    assert res.quantity_variance_units == 3
    assert any("Quantity Discrepancy" in d for d in res.discrepancy_details)


def test_three_way_matcher_missing_po():
    """Verify handling when no PO exists in the enterprise ledger."""
    item = LineItem(item_id="ITM-1", description="Monitors", quantity=2, unit_price_usd=100.0, total_price_usd=200.0)
    invoice = InvoicePayload(
        invoice_id="INV-TEST-04",
        vendor_id="V-99",
        vendor_name="Unknown Vendor",
        po_number="PO-NONEXISTENT",
        invoice_date="2026-10-01",
        due_date="2026-10-31",
        subtotal_usd=200.0,
        tax_usd=0.0,
        total_amount_usd=200.0,
        currency="USD",
        items=[item],
    )

    res = ThreeWayMatcher.reconcile(invoice, None)
    assert res.matched is False
    assert res.po_found is False


# =====================================================================
# 2. Machine Learning Anomaly Detection Tests
# =====================================================================

def test_anomaly_scorer_inlier_low_risk():
    """Verify standard operational transactions receive low risk scores."""
    scorer = AnomalyScorer()
    item = LineItem(item_id="ITM-1", description="Paper", quantity=10, unit_price_usd=15.0, total_price_usd=150.0)
    invoice = InvoicePayload(
        invoice_id="INV-LOW-01",
        vendor_id="V-1",
        vendor_name="PaperCo",
        po_number="PO-10",
        invoice_date="2026-10-01",
        due_date="2026-10-31",
        subtotal_usd=150.0,
        tax_usd=0.0,
        total_amount_usd=150.0,
        currency="USD",
        items=[item],
        vendor_country="IN",
        is_new_vendor=False,
    )
    po = PurchaseOrderRecord(
        po_number="PO-10",
        vendor_id="V-1",
        approved_total_usd=150.0,
        items=[item],
        grn_units_received={"ITM-1": 10},
    )
    match_res = ThreeWayMatcher.reconcile(invoice, po)
    risk = scorer.assess_risk(invoice, match_res)

    assert risk.risk_level == RiskLevelEnum.LOW
    assert risk.anomaly_detected is False
    assert risk.anomaly_score < 35.0


def test_anomaly_scorer_offshore_tax_haven_high_risk():
    """Verify offshore entity red flags trigger critical risk elevation."""
    scorer = AnomalyScorer()
    item = LineItem(item_id="ITM-1", description="Consulting", quantity=1, unit_price_usd=50000.0, total_price_usd=50000.0)
    invoice = InvoicePayload(
        invoice_id="INV-FRAUD-01",
        vendor_id="V-999",
        vendor_name="Offshore Shell Entity",
        po_number="PO-999",
        invoice_date="2026-10-01",
        due_date="2026-10-31",
        subtotal_usd=50000.0,
        tax_usd=0.0,
        total_amount_usd=50000.0,
        currency="USD",
        items=[item],
        vendor_country="BZ",  # Belize tax haven
        is_new_vendor=True,
    )
    po = PurchaseOrderRecord(
        po_number="PO-999",
        vendor_id="V-999",
        approved_total_usd=50000.0,
        items=[item],
        grn_units_received={"ITM-1": 1},
    )
    match_res = ThreeWayMatcher.reconcile(invoice, po)
    risk = scorer.assess_risk(invoice, match_res)

    assert risk.risk_level == RiskLevelEnum.CRITICAL
    assert risk.anomaly_detected is True
    assert risk.anomaly_score >= 85.0
    assert any("Offshore" in factor for factor in risk.risk_factors)


# =====================================================================
# 3. Privacy & PII Scrubber Tests
# =====================================================================

def test_pii_scrubber_pan_and_email():
    """Verify Indian PAN and vendor email scrubbing."""
    item = LineItem(item_id="ITM-1", description="Supplies", quantity=1, unit_price_usd=100.0, total_price_usd=100.0)
    invoice = InvoicePayload(
        invoice_id="INV-PII-01",
        vendor_id="V-1",
        vendor_name="Vendor India",
        po_number="PO-1",
        invoice_date="2026-10-01",
        due_date="2026-10-31",
        subtotal_usd=100.0,
        tax_usd=0.0,
        total_amount_usd=100.0,
        currency="USD",
        items=[item],
        vendor_pan="ABCDE1234F",
        vendor_contact_email="accounts.payable@vendor.in",
    )
    scrubbed, count = PIIScrubber.scrub_invoice(invoice)
    assert count >= 2
    assert scrubbed.vendor_pan == "[REDACTED_PAN]"
    assert scrubbed.vendor_contact_email == "[REDACTED_EMAIL]"


# =====================================================================
# 4. Corporate Governance Approval Router & Dual Currency Tests
# =====================================================================

def test_router_straight_through_processing():
    """Verify Tier 1 STP Auto-Approval for < $1,000 compliant invoices with INR conversion."""
    item = LineItem(item_id="ITM-1", description="Items", quantity=2, unit_price_usd=200.0, total_price_usd=400.0)
    invoice = InvoicePayload(
        invoice_id="INV-STP-01",
        vendor_id="V-1",
        vendor_name="OfficeSupplies",
        po_number="PO-1",
        invoice_date="2026-10-01",
        due_date="2026-10-31",
        subtotal_usd=400.0,
        tax_usd=0.0,
        total_amount_usd=400.0,
        currency="USD",
        items=[item],
    )
    po = PurchaseOrderRecord(
        po_number="PO-1",
        vendor_id="V-1",
        approved_total_usd=400.0,
        items=[item],
        grn_units_received={"ITM-1": 2},
    )
    matcher = ThreeWayMatcher.reconcile(invoice, po)
    scorer = AnomalyScorer()
    risk = scorer.assess_risk(invoice, matcher)
    decision = ApprovalRouter.route_decision(invoice, matcher, risk)

    assert decision.approval_tier == ApprovalTierEnum.TIER_1_STP
    assert decision.authorized is True
    assert decision.requires_hitl is False
    assert decision.total_amount_usd == 400.0
    assert decision.total_amount_inr == 400.0 * 86.50  # 34,600.00


def test_router_manager_review_tier():
    """Verify Tier 2 Manager Review for $1,000 - $10,000 compliant invoices."""
    item = LineItem(item_id="ITM-1", description="Servers", quantity=2, unit_price_usd=2500.0, total_price_usd=5000.0)
    invoice = InvoicePayload(
        invoice_id="INV-MGR-01",
        vendor_id="V-1",
        vendor_name="Hardware Direct",
        po_number="PO-2",
        invoice_date="2026-10-01",
        due_date="2026-10-31",
        subtotal_usd=5000.0,
        tax_usd=0.0,
        total_amount_usd=5000.0,
        currency="USD",
        items=[item],
    )
    po = PurchaseOrderRecord(
        po_number="PO-2",
        vendor_id="V-1",
        approved_total_usd=5000.0,
        items=[item],
        grn_units_received={"ITM-1": 2},
    )
    matcher = ThreeWayMatcher.reconcile(invoice, po)
    scorer = AnomalyScorer()
    risk = scorer.assess_risk(invoice, matcher)
    decision = ApprovalRouter.route_decision(invoice, matcher, risk)

    assert decision.approval_tier == ApprovalTierEnum.TIER_2_MANAGER
    assert decision.authorized is True
    assert decision.requires_hitl is True
    assert decision.total_amount_inr == 5000.0 * 86.50  # 432,500.00


def test_router_director_signoff_tier():
    """Verify Tier 3 Director Signoff for > $10,000 enterprise invoices."""
    item = LineItem(item_id="ITM-1", description="Compute Clusters", quantity=1, unit_price_usd=25000.0, total_price_usd=25000.0)
    invoice = InvoicePayload(
        invoice_id="INV-DIR-01",
        vendor_id="V-1",
        vendor_name="Enterprise Compute",
        po_number="PO-3",
        invoice_date="2026-10-01",
        due_date="2026-10-31",
        subtotal_usd=25000.0,
        tax_usd=0.0,
        total_amount_usd=25000.0,
        currency="USD",
        items=[item],
    )
    po = PurchaseOrderRecord(
        po_number="PO-3",
        vendor_id="V-1",
        approved_total_usd=25000.0,
        items=[item],
        grn_units_received={"ITM-1": 1},
    )
    matcher = ThreeWayMatcher.reconcile(invoice, po)
    scorer = AnomalyScorer()
    risk = scorer.assess_risk(invoice, matcher)
    decision = ApprovalRouter.route_decision(invoice, matcher, risk)

    assert decision.approval_tier == ApprovalTierEnum.TIER_3_DIRECTOR
    assert decision.authorized is True
    assert decision.requires_hitl is True
    assert decision.total_amount_inr == 25000.0 * 86.50  # 2,162,500.00


# =====================================================================
# 5. FastAPI End-to-End API Route Tests
# =====================================================================

def test_fastapi_health_endpoints():
    """Verify liveness and readiness probes."""
    live_resp = client.get("/health/live")
    assert live_resp.status_code == 200
    assert live_resp.json()["status"] == "LIVE"

    ready_resp = client.get("/health/ready")
    assert ready_resp.status_code == 200
    assert ready_resp.json()["status"] == "READY"
    assert "ml_anomaly_scorer" in ready_resp.json()["dependencies"]


def test_fastapi_process_invoice_full_flow():
    """Verify full end-to-end API audit processing."""
    payload = {
        "invoice": {
            "invoice_id": "INV-API-01",
            "vendor_id": "V-55",
            "vendor_name": "Cloud Providers Inc",
            "po_number": "PO-API-55",
            "invoice_date": "2026-10-01",
            "due_date": "2026-10-31",
            "subtotal_usd": 600.0,
            "tax_usd": 0.0,
            "total_amount_usd": 600.0,
            "currency": "USD",
            "items": [
                {
                    "item_id": "ITM-SVC",
                    "description": "Cloud Hosting",
                    "quantity": 1,
                    "unit_price_usd": 600.0,
                    "total_price_usd": 600.0
                }
            ],
            "vendor_country": "US",
            "vendor_contact_email": "billing@cloudproviders.com"
        },
        "purchase_order": {
            "po_number": "PO-API-55",
            "vendor_id": "V-55",
            "approved_total_usd": 600.0,
            "items": [
                {
                    "item_id": "ITM-SVC",
                    "description": "Cloud Hosting",
                    "quantity": 1,
                    "unit_price_usd": 600.0,
                    "total_price_usd": 600.0
                }
            ],
            "grn_units_received": {"ITM-SVC": 1}
        }
    }

    resp = client.post("/api/v1/audit/process", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["invoice_id"] == "INV-API-01"
    assert body["approval_tier"] == "TIER_1_STP_AUTO_APPROVED"
    assert body["authorized"] is True
    assert body["total_amount_usd"] == 600.0
    assert body["total_amount_inr"] == round(600.0 * 86.50, 2)
    assert body["pii_redactions_made"] >= 1


def test_fastapi_ledger_and_summary():
    """Verify audit ledger query and executive summary endpoints."""
    # Ledger query
    resp = client.get("/api/v1/audit/ledger")
    assert resp.status_code == 200
    ledger = resp.json()
    assert isinstance(ledger, list)
    assert len(ledger) >= 1

    # Executive summary
    summary_resp = client.get("/api/v1/audit/summary")
    assert summary_resp.status_code == 200
    summary = summary_resp.json()
    assert summary["total_invoices_audited"] >= 1
    assert summary["total_disbursed_inr"] > 0
    assert summary["exchange_rate_usd_to_inr"] == 86.50
