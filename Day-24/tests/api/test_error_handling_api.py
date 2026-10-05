"""
API Tests: Error Handling, Middleware & Observability Headers
Validates 404 responses, 422 validation errors, and tracing header injection.
"""


def test_404_not_found_endpoint(client):
    """Verify non-existent routes return 404 with correlation headers and rate limiter protects routes."""
    response = client.get("/api/v1/nonexistent/route")
    assert response.status_code == 404
    assert "X-Correlation-ID" in response.headers
    assert "X-Response-Time-Ms" in response.headers

    # Verify rate limiter active enforcement component
    rate_limiter = getattr(client.app.state, "rate_limiter", None)
    assert rate_limiter is not None
    for _ in range(rate_limiter.limit):
        rate_limiter.is_allowed("rate-test-client-unique")
    allowed, retry_after = rate_limiter.is_allowed("rate-test-client-unique")
    assert allowed is False
    assert retry_after > 0
    rate_limiter.reset()


def test_422_missing_required_fields(client, auth_headers):
    """Verify missing required body fields trigger 422 Unprocessable Entity."""
    response = client.post(
        "/api/v1/workflow/run",
        json={},  # Missing 'query'
        headers=auth_headers
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_correlation_id_generated_and_returned_in_header(client):
    """Verify each incoming request receives an auto-generated correlation ID header."""
    response = client.get("/health/live")
    assert response.status_code == 200
    cid = response.headers.get("X-Correlation-ID")
    assert cid is not None
    assert cid.startswith("CORR-")


def test_response_time_header_in_response(client):
    """Verify request latency in milliseconds is returned in response header."""
    response = client.get("/health/live")
    assert "X-Response-Time-Ms" in response.headers
    latency = float(response.headers["X-Response-Time-Ms"])
    assert latency >= 0.0
