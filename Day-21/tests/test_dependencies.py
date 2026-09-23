"""
Day 21 — Tests for Dependency Injection, Authentication & Authorization Roles
"""

from app.config import settings


def test_auth_missing_api_key_returns_401(client):
    """Verify missing API key on protected endpoint returns HTTP 401 Unauthorized."""
    payload = {"question": "What is the policy?"}
    response = client.post("/api/v1/query", json=payload)

    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "UNAUTHORIZED"
    assert "Missing required API key" in data["error"]["message"]


def test_auth_invalid_api_key_returns_401(client, test_keys):
    """Verify invalid API key returns HTTP 401 Unauthorized."""
    payload = {"question": "What is the policy?"}
    response = client.post("/api/v1/query", json=payload, headers={"X-API-Key": test_keys["invalid"]})

    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "UNAUTHORIZED"
    assert "Invalid API key" in data["error"]["message"]


def test_auth_valid_standard_key_success(client, test_keys):
    """Verify valid standard API key permits execution."""
    payload = {"question": "What is the leave entitlement?"}
    response = client.post("/api/v1/query", json=payload, headers={"X-API-Key": test_keys["standard"]})

    assert response.status_code == 200
    data = response.json()
    assert data["question"] == payload["question"]
    assert "results" in data


def test_auth_standard_key_forbidden_on_admin_endpoint(client, test_keys):
    """Verify valid standard key is rejected with HTTP 403 on admin-only endpoints."""
    response = client.get("/api/v1/audit/logs", headers={"X-API-Key": test_keys["standard"]})

    assert response.status_code == 403
    data = response.json()
    assert data["error"]["code"] == "FORBIDDEN"
    assert "Administrative privileges required" in data["error"]["message"]


def test_auth_admin_key_success_on_admin_endpoint(client, test_keys):
    """Verify admin key succeeds on admin endpoints."""
    response = client.get("/api/v1/audit/logs", headers={"X-API-Key": test_keys["admin"]})

    assert response.status_code == 200
    data = response.json()
    assert "total_records" in data
    assert "records" in data


def test_pagination_bounds_validation(client, test_keys):
    """Verify pagination validation limits (negative skip rejected, invalid order_by rejected)."""
    # Negative skip rejected
    resp = client.get(
        "/api/v1/audit/logs?skip=-1",
        headers={"X-API-Key": test_keys["admin"]}
    )
    assert resp.status_code == 422

    # Limit > 100 rejected
    resp_limit = client.get(
        "/api/v1/audit/logs?limit=101",
        headers={"X-API-Key": test_keys["admin"]}
    )
    assert resp_limit.status_code == 422

    # Invalid order_by rejected
    resp2 = client.get(
        "/api/v1/audit/logs?order_by=malicious_sql_injection",
        headers={"X-API-Key": test_keys["admin"]}
    )
    assert resp2.status_code == 422
    assert "Invalid order_by field" in resp2.json()["error"]["message"]


def test_dependency_override_in_tests(client):
    """Verify that dependencies can be cleanly overridden in tests."""
    from app.dependencies import verify_api_key
    from app.main import app

    app.dependency_overrides[verify_api_key] = lambda: {"role": "test_mock_role", "user": "test_mock_user"}

    try:
        # Request with NO API key header should succeed due to override
        resp = client.post("/api/v1/query", json={"question": "Testing override"})
        assert resp.status_code == 200
    finally:
        app.dependency_overrides.clear()
