"""Tests for Institutional Web Workbench, Raw Text Parser, Batch Demo & CSV Export Routes."""

from fastapi.testclient import TestClient


def test_dashboard_index_route(client: TestClient):
    """Verify that root URL '/' renders the institutional workbench HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "FinDoc-AuditEngine" in response.text
    assert "Disbursed Capital (INR)" in response.text
    assert "86.50" in response.text


def test_dashboard_alias_route(client: TestClient):
    """Verify that '/dashboard' route correctly serves the same workbench portal."""
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
    """Verify that institutional stylesheet is successfully served."""
    response = client.get("/static/css/dashboard.css")
    assert response.status_code == 200
    assert "--bg-primary" in response.text
    assert "IBM Plex Mono" in response.text


def test_static_js_assets_served(client: TestClient):
    """Verify that dynamic workbench JavaScript controller is successfully served."""
    response = client.get("/static/js/dashboard.js")
    assert response.status_code == 200
    assert "executeAudit" in response.text
    assert "renderLedgerTable" in response.text
    assert "collectLineItemsFromDOM" in response.text


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


def test_parse_raw_unstructured_invoice_endpoint(client: TestClient):
    """Verify that '/api/v1/audit/parse-raw' scrubs PII and extracts dynamic invoice fields."""
    raw = (
        "Invoice INV-5510 from Zenith Data Systems; PO: PO-5510; "
        "Total: $3,450.00; Country: US; Email: ap@zenithdata.com; PAN: ABCDE1234F"
    )
    res = client.post("/api/v1/audit/parse-raw", json={"raw_text": raw})
    assert res.status_code == 200
    body = res.json()
    assert body["pii_redactions_count"] >= 2
    assert "ap@zenithdata.com" not in body["sanitized_text"]
    assert "ABCDE1234F" not in body["sanitized_text"]
    assert body["extracted_fields"]["total_amount_usd"] == 3450.0


def test_demo_batch_and_csv_export_endpoints(client: TestClient):
    """Verify 1-click mentor demo batch execution and CSV compliance report export."""
    batch_res = client.post("/api/v1/audit/demo-batch")
    assert batch_res.status_code == 200
    decisions = batch_res.json()
    assert len(decisions) == 5

    csv_res = client.get("/api/v1/audit/export/csv")
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers["content-type"]
    lines = csv_res.text.strip().splitlines()
    assert len(lines) == 6  # 1 header + 5 rows
    assert "INV-1001" in csv_res.text

    clear_res = client.delete("/api/v1/audit/ledger/clear")
    assert clear_res.status_code == 200
    assert clear_res.json()["remaining"] == 0


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
