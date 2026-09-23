"""
Day 21 — Tests for Pydantic Schemas & Data Contracts
"""

import pytest
from pydantic import ValidationError
from app.schemas import (
    QueryRequest,
    BatchQueryRequest,
    ErrorResponse,
    DocumentRecord,
    HealthResponse
)


def test_query_request_valid():
    """Verify valid QueryRequest creation."""
    req = QueryRequest(question="What are the leave rules?", top_k=5, category="HR")
    assert req.question == "What are the leave rules?"
    assert req.top_k == 5
    assert req.category == "HR"


def test_query_request_empty_question_rejected():
    """Verify empty question triggers validation error."""
    with pytest.raises(ValidationError):
        QueryRequest(question="")


def test_query_request_oversized_question_rejected():
    """Verify questions exceeding 2000 chars are rejected."""
    long_q = "a" * 2001
    with pytest.raises(ValidationError):
        QueryRequest(question=long_q)


def test_query_request_top_k_bounds():
    """Verify top_k must be between 1 and 10."""
    with pytest.raises(ValidationError):
        QueryRequest(question="test", top_k=0)

    with pytest.raises(ValidationError):
        QueryRequest(question="test", top_k=11)


def test_batch_query_request_bounds():
    """Verify batch request must contain between 1 and 10 items."""
    # Empty list rejected
    with pytest.raises(ValidationError):
        BatchQueryRequest(queries=[])

    # 10 items accepted
    valid_batch = [QueryRequest(question=f"Q{i}") for i in range(10)]
    b_req = BatchQueryRequest(queries=valid_batch)
    assert len(b_req.queries) == 10

    # 11 items rejected
    too_many = [QueryRequest(question=f"Q{i}") for i in range(11)]
    with pytest.raises(ValidationError):
        BatchQueryRequest(queries=too_many)


def test_error_response_structure():
    """Verify standardized error envelope schema."""
    err = ErrorResponse(
        error={
            "code": "TEST_ERROR",
            "message": "Sample error message",
            "request_id": "test-req-123"
        }
    )
    assert err.error.code == "TEST_ERROR"
    assert err.error.message == "Sample error message"
    assert err.error.request_id == "test-req-123"
