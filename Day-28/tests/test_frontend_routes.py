"""Tests for Executive Frontend Web Portal and Supporting Static Routes."""

from fastapi.testclient import TestClient


def test_dashboard_index_route(client: TestClient):
    """Verify that root URL '/' renders the executive dashboard HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "FinDoc-AuditEngine" in response.text
    assert "Disbursed Capital (INR)" in response.text
    assert "86.50" in response.text


def test_dashboard_alias_route(client: TestClient):
    """Verify that '/dashboard' route correctly serves the same executive portal."""
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "FinDoc-AuditEngine" in response.text


def test_health_telemetry_endpoint(client: TestClient):
    """Verify that '/health' returns valid operational telemetry."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["pegged_usd_to_inr"] == 86.50
    assert "models" in data
    assert data["models"]["anomaly_detector"] == "IsolationForest_v2.0"


def test_static_css_assets_served(client: TestClient):
    """Verify that executive stylesheet is successfully served."""
    response = client.get("/static/css/dashboard.css")
    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"] or "stylesheet" in response.text or "body" in response.text
    assert "--bg-primary" in response.text


def test_static_js_assets_served(client: TestClient):
    """Verify that dashboard JavaScript controller is successfully served."""
    response = client.get("/static/js/dashboard.js")
    assert response.status_code == 200
    assert "executeAudit" in response.text
    assert "renderLedgerTable" in response.text


def test_presets_endpoint(client: TestClient):
    """Verify that '/api/v1/audit/presets' returns the 5 enterprise benchmark invoices."""
    response = client.get("/api/v1/audit/presets")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5
    ids = [item["invoice"]["invoice_id"] for item in data]
    assert "INV-1001" in ids
    assert "INV-1005" in ids


def test_summary_and_ledger_endpoints(client: TestClient):
    """Verify summary KPIs and ledger filtering."""
    summary_res = client.get("/api/v1/audit/summary")
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert "total_invoices_audited" in summary
    assert "total_disbursed_usd" in summary
    assert summary["exchange_rate_applied"] == 86.50

    ledger_res = client.get("/api/v1/audit/ledger")
    assert ledger_res.status_code == 200
    assert isinstance(ledger_res.json(), list)
