"""
API Tests: Linkific Finance Workflow Automation Endpoint
Validates /api/v1/finance/invoice-approval against business threshold rules and PO matching.
"""


def test_finance_stp_invoice_api(client, auth_headers, sample_finance_request):
    """Verify STP approval (< $1,000 with valid PO) via HTTP API."""
    response = client.post(
        "/api/v1/finance/invoice-approval",
        json=sample_finance_request,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"
    assert data["auto_approved"] is True
    assert data["approval_tier"] == "straight_through_processing"
    assert data["matched_po"] is True
    assert data["audit_id"].startswith("AUD-FIN-")


def test_finance_manager_approval_api(client, auth_headers, sample_finance_request):
    """Verify Manager approval escalation ($1,000 - $10,000) via HTTP API."""
    req = dict(sample_finance_request)
    req["amount"] = 4500.00
    response = client.post(
        "/api/v1/finance/invoice-approval",
        json=req,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending_approval"
    assert data["auto_approved"] is False
    assert data["approval_tier"] == "manager_approval"
    assert "Finance Department Manager" in data["required_signers"]


def test_finance_director_approval_api(client, auth_headers, sample_finance_request):
    """Verify Director approval escalation (> $10,000) via HTTP API."""
    req = dict(sample_finance_request)
    req["amount"] = 35000.00
    response = client.post(
        "/api/v1/finance/invoice-approval",
        json=req,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending_approval"
    assert data["auto_approved"] is False
    assert data["approval_tier"] == "director_approval"
    assert "Finance Director" in data["required_signers"]


def test_finance_invalid_po_api(client, auth_headers, sample_finance_request):
    """Verify invalid PO reference causes invoice to be flagged."""
    req = dict(sample_finance_request)
    req["po_number"] = "NON-PO-REF"
    response = client.post(
        "/api/v1/finance/invoice-approval",
        json=req,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "flagged"
    assert data["approval_tier"] == "rejected"
    assert data["matched_po"] is False
