"""
Day 21 — Tests for Batch Query Processing, Limits & Concurrency Constraints
"""


def test_batch_query_exceeding_max_limit_fails(client, test_keys):
    """Verify batch request exceeding max batch limit (> 10) returns 400 Bad Request."""
    too_many_queries = [{"question": f"Question {i}"} for i in range(11)]
    response = client.post(
        "/api/v1/batch-query",
        json={"queries": too_many_queries},
        headers={"X-API-Key": test_keys["standard"]}
    )
    # Pydantic or endpoint rejects > 10 items
    assert response.status_code in (400, 422)


def test_batch_query_preserves_order(client, test_keys):
    """Verify concurrent batch query results preserve exact input order."""
    questions = [
        "leave policy rules",
        "remote hardware security",
        "engineering code review standards",
        "data privacy classification"
    ]
    payload = {"queries": [{"question": q} for q in questions]}

    response = client.post(
        "/api/v1/batch-query",
        json=payload,
        headers={"X-API-Key": test_keys["standard"]}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_queries"] == 4
    for i in range(4):
        item = data["results"][i]
        assert item["index"] == i
        assert item["status"] == "success"
        assert item["result"]["question"] == questions[i]
