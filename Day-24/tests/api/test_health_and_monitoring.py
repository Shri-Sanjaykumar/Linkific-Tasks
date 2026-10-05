"""
API Tests: Core Probes & Prometheus Monitoring
Validates /, /health/live, /health/ready, and /metrics HTTP endpoints.
"""


def test_root_endpoint(client):
    """Verify root GET endpoint returns service identity and probe locations."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert data["status"] == "OPERATIONAL"
    assert "/health/live" in data["probes"]["liveness"]
    assert "/metrics" in data["probes"]["metrics"]


def test_liveness_probe_endpoint(client):
    """Verify liveness probe returns HTTP 200 and uptime."""
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"
    assert "uptime_seconds" in data
    assert data["uptime_seconds"] >= 0.0


def test_readiness_probe_endpoint(client):
    """Verify readiness probe verifies all core subsystems before reporting ready."""
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "document_corpus" in data["components"]
    assert "logging_subsystem" in data["components"]
    assert "workflow_engine" in data["components"]


def test_prometheus_metrics_endpoint(client):
    """Verify /metrics returns official Prometheus text format with registered counters."""
    # Generate some traffic first
    client.get("/")
    client.get("/health/live")

    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    text = response.text

    assert "linkific_uptime_seconds" in text
    assert "linkific_http_requests_total" in text
    assert "linkific_active_workflows" in text
