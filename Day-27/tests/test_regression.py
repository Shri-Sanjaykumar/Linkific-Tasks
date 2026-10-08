"""Day 27 system regression tests for the FinDoc-AuditEngine MVP."""

from fastapi.testclient import TestClient

from app.main import app
from app.models import InvoicePayload, LineItem, PurchaseOrderRecord
from app.services.matcher import ReconciliationMatcher
from app.services.router import ApprovalRouter
from app.services.anomaly_detector import AnomalyScorer
from app.core.privacy import FinancialPrivacyScrubber

client = TestClient(app)


def make_invoice(amount=500.0, vendor="Regression Vendor", country="IN", new=False):
    item = LineItem(item_id="REG-1", description="Service", quantity=1,
                    unit_price_usd=amount, total_price_usd=amount)
    return InvoicePayload(
        invoice_id="REG-INV",
        vendor_id="REG-V",
        vendor_name=vendor,
        po_number="REG-PO",
        invoice_date="2026-10-08",
        due_date="2026-10-31",
        subtotal_usd=amount,
        tax_usd=0.0,
        total_amount_usd=amount,
        currency="USD",
        items=[item],
        vendor_country=country,
        is_new_vendor=new,
    )


def make_po(invoice):
    return PurchaseOrderRecord(
        po_number="REG-PO",
        vendor_id="REG-V",
        approved_total_usd=invoice.total_amount_usd,
        items=invoice.items,
        grn_units_received={"REG-1": 1},
        grn_units_rejected={"REG-1": 0},
    )


def test_regression_matcher_is_deterministic():
    invoice = make_invoice()
    po = make_po(invoice)
    first = ReconciliationMatcher.match(invoice, po)
    second = ReconciliationMatcher.match(invoice, po)
    assert first.model_dump() == second.model_dump()


def test_regression_missing_grn_defaults_to_po_quantity():
    invoice = make_invoice(amount=250.0)
    po = make_po(invoice)
    po.grn_units_received = {}
    result = ReconciliationMatcher.match(invoice, po)
    assert result.matched is True
    assert result.quantity_variance_units == 0


def test_regression_privacy_scrubs_bank_account():
    text = "Vendor account 123456789012 and email finance@example.com"
    masked, count, _ = FinancialPrivacyScrubber.scrub_text(text)
    assert "123456789012" not in masked
    assert "finance@example.com" not in masked
    assert count >= 2


def test_regression_ml_feature_vector_shape():
    invoice = make_invoice()
    po = make_po(invoice)
    match = ReconciliationMatcher.match(invoice, po)
    features = AnomalyScorer().extract_features(invoice, match)
    assert features.shape == (1, 5)


def test_regression_api_can_register_and_reuse_po():
    invoice = make_invoice(amount=700.0)
    po = make_po(invoice)
    response = client.post("/api/v1/audit/po/register", json=po.model_dump())
    assert response.status_code == 201

    payload = {"invoice": invoice.model_dump()}
    response = client.post("/api/v1/audit/process", json=payload)
    assert response.status_code == 200
    assert response.json()["authorized"] is True


def test_regression_director_threshold_routes_correctly():
    invoice = make_invoice(amount=10001.0)
    po = make_po(invoice)
    match = ReconciliationMatcher.match(invoice, po)
    risk = AnomalyScorer().assess_risk(invoice, match)
    decision = ApprovalRouter.route_decision(invoice, match, risk)
    assert decision.approval_tier.value == "TIER_3_DIRECTOR_SIGNOFF"
    assert decision.requires_hitl is True


def test_regression_critical_offshore_invoice_is_blocked():
    invoice = make_invoice(amount=50000.0, vendor="Offshore Vendor", country="BZ", new=True)
    po = make_po(invoice)
    match = ReconciliationMatcher.match(invoice, po)
    risk = AnomalyScorer().assess_risk(invoice, match)
    decision = ApprovalRouter.route_decision(invoice, match, risk)
    assert decision.authorized is False
    assert decision.approval_tier.value == "FROZEN_FRAUD_RISK"
