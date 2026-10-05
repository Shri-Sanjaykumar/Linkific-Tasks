"""
API Tests: Authentication, Authorization & Security
Validates API Key protection on enterprise endpoints and CORS policy enforcement.
"""


def test_missing_api_key_returns_401(client):
    """Verify protected endpoints reject requests lacking X-API-Key header."""
    response = client.get("/api/v1/system/info")
    assert response.status_code == 401
    assert "Invalid or missing X-API-Key" in response.json()["detail"]


def test_invalid_api_key_returns_401(client):
    """Verify protected endpoints reject requests with wrong API keys."""
    response = client.get("/api/v1/system/info", headers={"X-API-Key": "wrong-key-value"})
    assert response.status_code == 401
    assert "Invalid or missing X-API-Key" in response.json()["detail"]


def test_valid_api_key_authorizes_system_info(client, auth_headers):
    """Verify authorized requests access system info with safe masked fields."""
    response = client.get("/api/v1/system/info", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "app_name" in data
    assert "version" in data
    assert "corpus_document_count" in data
    assert data["corpus_document_count"] > 0


def test_cors_preflight_and_response_headers(client):
    """Verify CORS headers allow trusted origins and strictly deny untrusted origins."""
    response = client.get("/", headers={"Origin": "https://www.linkific.in"})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "https://www.linkific.in"

    untrusted_resp = client.get("/", headers={"Origin": "https://evil.example"})
    assert untrusted_resp.status_code == 200
    assert "access-control-allow-origin" not in untrusted_resp.headers
