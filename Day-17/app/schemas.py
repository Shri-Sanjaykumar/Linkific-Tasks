"""
Day 17 — FastAPI RAG Application Schemas
Pydantic models for request validation and structured API responses.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ------------------------------------------------------------------------------
# Health & Status Schemas
# ------------------------------------------------------------------------------
class HealthResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "healthy"})
    application: str = Field(..., json_schema_extra={"example": "Linkific RAG API"})
    version: str = Field(..., json_schema_extra={"example": "1.0.0"})
    documents_indexed: int = Field(..., json_schema_extra={"example": 2})
    total_chunks: int = Field(..., json_schema_extra={"example": 35})
    embedding_model: str = Field(..., json_schema_extra={"example": "sentence-transformers/all-MiniLM-L6-v2"})
    generator_model: str = Field(..., json_schema_extra={"example": "google-t5/t5-small"})


class WelcomeResponse(BaseModel):
    message: str
    status: str
    docs_url: str
    endpoints: Dict[str, str]


# ------------------------------------------------------------------------------
# Document & Upload Schemas
# ------------------------------------------------------------------------------
class UploadResponse(BaseModel):
    document_id: str
    filename: str
    file_type: str
    file_size_bytes: int
    pages_count: int
    chunks_count: int
    chunk_size: int
    overlap: int
    message: str


class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    file_type: str
    file_size_bytes: int
    pages_count: int
    chunks_count: int
    upload_timestamp: str


class DocumentListResponse(BaseModel):
    total_documents: int
    documents: List[DocumentInfo]


class DeleteDocumentResponse(BaseModel):
    document_id: str
    filename: str
    chunks_removed: int
    message: str


# ------------------------------------------------------------------------------
# RAG Query & Answer Schemas
# ------------------------------------------------------------------------------
class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=3, description="User query to answer from indexed documents", json_schema_extra={"example": "What is the daily task submission deadline?"})
    top_k: Optional[int] = Field(default=2, ge=1, le=5, description="Number of relevant chunks to retrieve")


class SourceChunk(BaseModel):
    document_id: str
    filename: str
    page_number: int
    chunk_id: int
    similarity_score: float
    cosine_distance: float
    text_snippet: str


class AnswerResponse(BaseModel):
    question: str
    answer: str
    total_sources: int
    sources: List[SourceChunk]


# ------------------------------------------------------------------------------
# Error Schema
# ------------------------------------------------------------------------------
class ErrorDetail(BaseModel):
    detail: str
    error_code: str
    status_code: int
