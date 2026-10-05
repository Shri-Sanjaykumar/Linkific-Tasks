"""
API Tests: Multi-Agent Workflow HTTP Endpoint
Validates /api/v1/workflow/run for streamlined, comprehensive, and failure scenarios.
"""


def test_run_workflow_streamlined_api(client, auth_headers, sample_workflow_request):
    """Verify streamlined multi-agent execution via authenticated HTTP POST."""
    response = client.post(
        "/api/v1/workflow/run",
        json=sample_workflow_request,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "completed"
    assert data["critic_approved"] is True
    assert data["milestones_completed"] >= 3
    assert data["communication_hops"] >= 4
    assert len(data["final_answer"]) > 20
    assert "report" in data
    assert data["report"]["report_id"].startswith("REP-")


def test_run_workflow_comprehensive_api(client, auth_headers):
    """Verify comprehensive multi-agent execution via authenticated HTTP POST."""
    payload = {
        "query": "What are the protocols for Severity 1 production incident escalation, CI/CD code review SLAs, and test coverage gates?",
        "mode": "comprehensive"
    }
    response = client.post(
        "/api/v1/workflow/run",
        json=payload,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "completed"
    assert data["critic_approved"] is True
    assert data["milestones_completed"] >= 5
    assert data["communication_hops"] >= 6


def test_run_workflow_with_custom_correlation_id(client, auth_headers):
    """Verify client-supplied correlation ID is propagated and returned in response headers and payload."""
    custom_cid = "CORR-CLIENT-FLOW-888"
    req_headers = dict(auth_headers)
    req_headers["X-Correlation-ID"] = custom_cid
    payload = {
        "query": "What are the rules regarding Kubernetes orchestration and RTO?",
        "mode": "streamlined",
        "correlation_id": custom_cid
    }
    response = client.post(
        "/api/v1/workflow/run",
        json=payload,
        headers=req_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["correlation_id"] == custom_cid
    assert response.headers.get("X-Correlation-ID") == custom_cid


def test_run_workflow_invalid_mode_returns_422(client, auth_headers):
    """Verify Pydantic validator rejects unsupported execution modes with HTTP 422."""
    payload = {
        "query": "Valid length query",
        "mode": "nonexistent_mode"
    }
    response = client.post(
        "/api/v1/workflow/run",
        json=payload,
        headers=auth_headers
    )
    assert response.status_code == 422


def test_run_workflow_short_query_returns_422(client, auth_headers):
    """Verify Pydantic validator rejects queries below minimum length threshold."""
    payload = {
        "query": "ab",
        "mode": "streamlined"
    }
    response = client.post(
        "/api/v1/workflow/run",
        json=payload,
        headers=auth_headers
    )
    assert response.status_code == 422
