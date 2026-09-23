"""
Day 21 — Tests for Legacy Unversioned Routes & Backward Compatibility (Day 17 Mapping)
"""


def test_legacy_root(client):
    """Verify legacy GET / returns welcome payload and service discovery."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "endpoints" in data
    assert "GET /api/v1/health" in data["endpoints"]


def test_legacy_health(client):
    """Verify legacy GET /health returns system health."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "total_indexed_documents" in data


def test_legacy_documents(client):
    """Verify legacy GET /documents returns indexed documents."""
    response = client.get("/documents")
    assert response.status_code == 200
    data = response.json()
    assert data["total_documents"] >= 5
    assert len(data["documents"]) >= 5


def test_legacy_ask_endpoint(client):
    """Verify legacy POST /ask matching Day 17 Q&A contract."""
    response = client.post("/ask", json={"question": "What are core collaboration hours?"})
    assert response.status_code == 200
    data = response.json()
    assert "question" in data
    assert "answer" in data
    assert "sources" in data
    assert len(data["sources"]) > 0


def test_legacy_ask_empty_question_fails(client):
    """Verify legacy POST /ask with empty question returns 400 Bad Request."""
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 400


def test_sync_query_baseline_endpoint(client):
    """Verify POST /sync/query executes synchronous baseline query."""
    payload = {"question": "hardware security guidelines", "top_k": 2}
    response = client.post("/sync/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["execution_mode"] == "sync"
    assert data["matched_count"] > 0
    assert "duration_ms" in data
