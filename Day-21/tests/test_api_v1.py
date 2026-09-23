"""
Day 21 — Tests for Versioned API Endpoints (/api/v1/...)
"""


def test_v1_health_endpoint(client):
    """Verify GET /api/v1/health returns operational status."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["worker_mode"] == "asynchronous_event_loop"
    assert data["total_indexed_documents"] >= 5


def test_v1_query_endpoint(client, test_keys):
    """Verify POST /api/v1/query executes non-blocking retrieval."""
    payload = {"question": "What is the policy on code reviews?", "top_k": 2}
    response = client.post(
        "/api/v1/query",
        json=payload,
        headers={"X-API-Key": test_keys["standard"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["execution_mode"] == "async"
    assert data["matched_count"] > 0
    assert len(data["results"]) <= 2
    assert "duration_ms" in data


def test_v1_batch_query_endpoint(client, test_keys):
    """Verify POST /api/v1/batch-query processes multiple queries concurrently."""
    batch_payload = {
        "queries": [
            {"question": "leave policy", "top_k": 2},
            {"question": "remote hardware", "top_k": 2},
            {"question": "onboarding guidelines", "top_k": 2}
        ]
    }
    response = client.post(
        "/api/v1/batch-query",
        json=batch_payload,
        headers={"X-API-Key": test_keys["standard"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_queries"] == 3
    assert data["successful_queries"] == 3
    assert data["failed_queries"] == 0
    assert len(data["results"]) == 3
    assert data["results"][0]["index"] == 0
    assert data["results"][1]["index"] == 1
    assert data["results"][2]["index"] == 2


def test_v1_metrics_endpoint(client):
    """Verify GET /api/v1/metrics returns live telemetry."""
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_requests_processed" in data
    assert "average_process_time_ms" in data
    assert "p95_process_time_ms" in data
    assert "uptime_seconds" in data
