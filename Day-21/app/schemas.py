"""
Day 21 — Pydantic Schemas & Data Contracts
Defines strictly-typed request and response contracts, validation limits,
and unified error envelopes for all versioned and legacy endpoints.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


# ------------------------------------------------------------------------------
# Unified Error Envelopes
# ------------------------------------------------------------------------------
class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code (e.g. INVALID_API_KEY, VALIDATION_ERROR)")
    message: str = Field(..., description="Safe human-readable error description without sensitive stack traces")
    request_id: Optional[str] = Field(default=None, description="Correlation ID associated with the failed request")
    details: Optional[Any] = Field(default=None, description="Granular error items, e.g. Pydantic field validation errors")


class ErrorResponse(BaseModel):
    error: ErrorDetail


# ------------------------------------------------------------------------------
# Core System & Diagnostics Schemas
# ------------------------------------------------------------------------------
class HealthResponse(BaseModel):
    status: str = Field(default="healthy", description="Operational health status")
    uptime_seconds: float = Field(..., description="Total system uptime in seconds")
    version: str = Field(..., description="API version string")
    environment: str = Field(..., description="Runtime environment (development/testing/production)")
    worker_mode: str = Field(..., description="Event loop operational mode (async/sync)")
    total_indexed_documents: int = Field(default=0, description="Number of documents currently available in corpus")


class WelcomeResponse(BaseModel):
    message: str
    status: str
    docs_url: str
    version: str
    endpoints: Dict[str, str]


# ------------------------------------------------------------------------------
# Document & Query Schemas
# ------------------------------------------------------------------------------
class DocumentRecord(BaseModel):
    id: str = Field(..., description="Document unique identifier (e.g. DOC-POL-001)")
    title: str = Field(..., description="Title of the document")
    category: str = Field(..., description="Organizational category")
    content: str = Field(..., description="Document text content")
    author: str = Field(..., description="Author or department")
    version: str = Field(..., description="Document version")
    word_count: int = Field(..., description="Total word count in content")
    score: float = Field(default=0.0, description="Relevance similarity score (0.0 to 1.0)")


class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Search inquiry or question to evaluate against document corpus"
    )
    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum number of top matching document passages to return"
    )
    category: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Optional category filter (e.g. 'Human Resources', 'Engineering')"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "question": "What is the remote work policy?",
                "top_k": 3
            }
        }
    }


class QueryResponse(BaseModel):
    question: str
    matched_count: int
    results: List[DocumentRecord]
    execution_mode: str = Field(..., description="'async' or 'sync'")
    duration_ms: float
    request_id: Optional[str] = None


# ------------------------------------------------------------------------------
# Batch Query Schemas
# ------------------------------------------------------------------------------
class BatchQueryRequest(BaseModel):
    queries: List[QueryRequest] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="List of independent queries to process concurrently (maximum 10 queries)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "queries": [
                    {"question": "What is the remote work policy?", "top_k": 2},
                    {"question": "What are the core hours?", "top_k": 2},
                    {"question": "What hardware allowance is provided?", "top_k": 2}
                ]
            }
        }
    }


class BatchQueryItemResult(BaseModel):
    index: int = Field(..., description="Zero-based index of query in request array")
    status: str = Field(..., description="'success', 'error', or 'timeout'")
    result: Optional[QueryResponse] = None
    error: Optional[str] = None


class BatchQueryResponse(BaseModel):
    total_queries: int
    successful_queries: int
    failed_queries: int
    results: List[BatchQueryItemResult]
    total_duration_ms: float
    request_id: Optional[str] = None


# ------------------------------------------------------------------------------
# Background Audit Logging Schemas
# ------------------------------------------------------------------------------
class AuditRecord(BaseModel):
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp of event")
    request_id: str = Field(..., description="Unique correlation ID for tracing")
    event: str = Field(..., description="Event name (e.g. query_executed, batch_executed)")
    endpoint: str = Field(..., description="API endpoint path")
    status: str = Field(..., description="'success', 'validation_error', or 'error'")
    duration_ms: float = Field(..., description="Total processing time in milliseconds")
    client_ip: Optional[str] = Field(default=None, description="Client IP address")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Supplementary contextual details")


class AuditLogListResponse(BaseModel):
    total_records: int
    returned_records: int
    skip: int
    limit: int
    records: List[AuditRecord]


# ------------------------------------------------------------------------------
# Metrics & Telemetry Schemas
# ------------------------------------------------------------------------------
class MetricsResponse(BaseModel):
    total_requests_processed: int
    average_process_time_ms: float
    p95_process_time_ms: float
    uptime_seconds: float
    active_worker_threads: int
