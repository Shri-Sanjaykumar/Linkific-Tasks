"""
Day 21 — Tests for Middleware Execution, Latency Timing & Correlation IDs
"""

import re
from app.middleware import metrics_tracker


def test_middleware_injects_headers(client):
    """Verify middleware injects X-Request-ID and X-Process-Time-Ms on every response."""
    response = client.get("/")
    assert response.status_code == 200

    # 1. Request ID header check
    assert "X-Request-ID" in response.headers
    req_id = response.headers["X-Request-ID"]
    assert len(req_id) > 0

    # 2. Timing header check
    assert "X-Process-Time-Ms" in response.headers
    timing_str = response.headers["X-Process-Time-Ms"]
    timing_float = float(timing_str)
    assert timing_float >= 0.0


def test_middleware_preserves_valid_client_correlation_id(client):
    """Verify client-supplied valid X-Request-ID is preserved and propagated."""
    custom_id = "client-trace-abc-12345"
    response = client.get("/", headers={"X-Request-ID": custom_id})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == custom_id


def test_middleware_sanitizes_invalid_client_correlation_id(client):
    """Verify oversized or malformed client X-Request-ID is replaced with a safe UUID."""
    malformed_id = "bad@id!" * 20  # Over 64 chars and invalid chars
    response = client.get("/", headers={"X-Request-ID": malformed_id})

    assert response.status_code == 200
    returned_id = response.headers["X-Request-ID"]
    assert returned_id != malformed_id
    # Should be valid UUID4 format
    assert re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", returned_id)


def test_middleware_tracks_metrics(client):
    """Verify middleware accumulates telemetry in metrics_tracker."""
    initial_count = metrics_tracker.total_requests
    client.get("/")
    client.get("/health")
    assert metrics_tracker.total_requests >= initial_count + 2
