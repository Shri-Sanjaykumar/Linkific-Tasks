"""
Day 21 — Tests for Global Exception Handling & Error Envelopes
"""

from unittest.mock import patch
from app.dependencies import get_async_service


def test_404_not_found_envelope(client):
    """Verify non-existent route returns standard ErrorResponse envelope with code NOT_FOUND."""
    response = client.get("/api/v1/non_existent_path")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert "request_id" in data["error"]


def test_422_validation_error_envelope(client, test_keys):
    """Verify request validation failure returns standard ErrorResponse envelope with details."""
    # Sending invalid body (top_k < 1)
    response = client.post(
        "/api/v1/query",
        json={"question": "valid question", "top_k": -5},
        headers={"X-API-Key": test_keys["standard"]}
    )
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "details" in data["error"]
    assert len(data["error"]["details"]) > 0


def test_422_missing_required_field_envelope(client, test_keys):
    """Verify missing required field 'question' returns standard 422 validation envelope."""
    response = client.post(
        "/api/v1/query",
        json={"top_k": 3},  # missing 'question'
        headers={"X-API-Key": test_keys["standard"]}
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    field_names = [d["field"] for d in data["error"]["details"]]
    assert any("question" in f for f in field_names)


def test_422_invalid_json_body_envelope(client, test_keys):
    """Verify malformed JSON body returns clean validation envelope without server crash."""
    response = client.post(
        "/api/v1/query",
        content="This is plain text not JSON {",
        headers={"Content-Type": "application/json", "X-API-Key": test_keys["standard"]}
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_500_general_exception_envelope(test_keys):
    """Verify unexpected service exception returns HTTP 500 without leaking stack traces."""
    class CrashingService:
        async def query_async(self, *args, **kwargs):
            raise RuntimeError("Database connection suddenly dropped: secret_db_pass@10.0.0.1")

    from app.main import app
    from fastapi.testclient import TestClient

    app.dependency_overrides[get_async_service] = lambda: CrashingService()

    try:
        # raise_server_exceptions=False tells TestClient to return HTTP 500 response instead of re-raising
        with TestClient(app, raise_server_exceptions=False) as safe_client:
            response = safe_client.post(
                "/api/v1/query",
                json={"question": "Trigger crash"},
                headers={"X-API-Key": test_keys["standard"]}
            )
            assert response.status_code == 500
            data = response.json()
            assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
            # Ensure secret password or internal details are NOT leaked to client
            assert "secret_db_pass" not in response.text
            assert "Traceback" not in response.text
    finally:
        app.dependency_overrides.clear()


def test_error_envelope_does_not_leak_stack_trace(client, test_keys):
    """Verify error responses never expose Python file paths or stack traces."""
    response = client.post(
        "/api/v1/query",
        json={"question": ""},  # empty string triggers validation error
        headers={"X-API-Key": test_keys["standard"]}
    )
    raw_text = response.text
    # Should not contain Python traceback artifacts
    assert "Traceback (most recent call last)" not in raw_text
    assert "site-packages" not in raw_text
    assert "C:\\" not in raw_text
