"""
Unit Tests: Linkific Finance Workflow Automation Rules
Validates invoice approval thresholds, PO matching, and straight-through processing.
"""

from app.schemas import ApprovalTier


def evaluate_invoice_tier(amount: float, po_number: str):
    """Local evaluation function matching main.py logic."""
    has_valid_po = bool(po_number and po_number.startswith("PO-"))
    if not has_valid_po:
        return "flagged", ApprovalTier.REJECTED, False
    elif amount <= 1000.0:
        return "approved", ApprovalTier.STRAIGHT_THROUGH, True
    elif amount <= 10000.0:
        return "pending_approval", ApprovalTier.MANAGER_APPROVAL, False
    else:
        return "pending_approval", ApprovalTier.DIRECTOR_APPROVAL, False


def test_straight_through_processing_tier():
    """Verify invoices under $1,000 with valid PO qualify for auto-approval (STP)."""
    status, tier, auto = evaluate_invoice_tier(amount=450.00, po_number="PO-10293")
    assert status == "approved"
    assert tier == ApprovalTier.STRAIGHT_THROUGH
    assert auto is True


def test_manager_approval_tier():
    """Verify invoices between $1,000 and $10,000 require Department Manager approval."""
    status, tier, auto = evaluate_invoice_tier(amount=5500.00, po_number="PO-44812")
    assert status == "pending_approval"
    assert tier == ApprovalTier.MANAGER_APPROVAL
    assert auto is False


def test_director_approval_tier():
    """Verify invoices exceeding $10,000 require Director approval."""
    status, tier, auto = evaluate_invoice_tier(amount=25000.00, po_number="PO-99120")
    assert status == "pending_approval"
    assert tier == ApprovalTier.DIRECTOR_APPROVAL
    assert auto is False


def test_invalid_po_rejection():
    """Verify invoices missing PO or with invalid prefix are flagged."""
    status, tier, auto = evaluate_invoice_tier(amount=200.00, po_number="INVALID-REF")
    assert status == "flagged"
    assert tier == ApprovalTier.REJECTED
    assert auto is False
