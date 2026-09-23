"""
Day 21 — Legacy & Baseline API Routes
Provides backward-compatible endpoints matching Day-17 signatures (GET /, GET /health, GET /documents, POST /ask)
and provides the synchronous baseline endpoint (POST /sync/query) for performance benchmarking.
"""

import time
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException, status
from ..schemas import WelcomeResponse, HealthResponse, QueryRequest, QueryResponse, DocumentRecord
from ..config import settings
from ..services.sync_service import SyncDataService
from ..services.async_service import AsyncDataService

legacy_router = APIRouter(tags=["Legacy & Compatibility"])

# Initialize services with corpus path
sync_service = SyncDataService(corpus_path=settings.CORPUS_FILE)
async_service = AsyncDataService(corpus_path=settings.CORPUS_FILE)


@legacy_router.get("/", response_model=WelcomeResponse)
async def legacy_root():
    """Welcome endpoint providing service discovery and version metadata."""
    return {
        "message": "Welcome to Linkific Enterprise AI Service — Day 21 (Async & Modular Architecture)",
        "status": "online",
        "docs_url": "/docs",
        "version": settings.APP_VERSION,
        "endpoints": {
            "GET /": "API welcome and service discovery",
            "GET /health": "Legacy system health check",
            "GET /documents": "Legacy document registry listing",
            "POST /ask": "Legacy question-answering endpoint",
            "POST /sync/query": "Synchronous baseline query endpoint (for benchmarking)",
            "GET /api/v1/health": "Versioned health check",
            "POST /api/v1/query": "Versioned asynchronous query with audit logging",
            "POST /api/v1/batch-query": "Versioned concurrent batch query",
            "GET /api/v1/audit/logs": "Versioned audit log inspection",
            "GET /api/v1/metrics": "Versioned system performance telemetry"
        }
    }


@legacy_router.get("/health", response_model=HealthResponse)
async def legacy_health():
    """Legacy health check endpoint."""
    docs = sync_service.load_documents()
    return {
        "status": "healthy",
        "uptime_seconds": round(time.time() - getattr(settings, "_start_time", time.time()), 2),
        "version": settings.APP_VERSION,
        "environment": settings.LINKIFIC_ENV,
        "worker_mode": "hybrid_async_sync",
        "total_indexed_documents": len(docs)
    }


@legacy_router.get("/documents")
async def legacy_documents():
    """Legacy endpoint listing all documents in the corpus."""
    docs = sync_service.load_documents()
    return {
        "total_documents": len(docs),
        "documents": [
            {
                "document_id": d.get("id"),
                "filename": f"{d.get('id')}.txt",
                "title": d.get("title"),
                "category": d.get("category"),
                "word_count": d.get("word_count")
            }
            for d in docs
        ]
    }


@legacy_router.post("/ask")
async def legacy_ask(request: Dict[str, Any]):
    """
    Legacy question endpoint matching Day-17's POST /ask structure.
    Accepts {'question': str, 'top_k': Optional[int]}.
    """
    q = request.get("question")
    if not q or not str(q).strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Field 'question' is required and cannot be empty."
        )

    top_k = request.get("top_k", 2)
    matches = sync_service.query(question=str(q), top_k=top_k, simulate_io_delay=0.0)

    if not matches:
        return {
            "question": q,
            "answer": "No relevant document passages found matching your question.",
            "sources": []
        }

    top_doc = matches[0]
    return {
        "question": q,
        "answer": f"Based on {top_doc.get('title')}: {top_doc.get('content')}",
        "sources": [
            {
                "document_id": m.get("id"),
                "title": m.get("title"),
                "category": m.get("category"),
                "similarity_score": m.get("score")
            }
            for m in matches
        ]
    }


# ------------------------------------------------------------------------------
# Synchronous Baseline Benchmark Endpoint
# ------------------------------------------------------------------------------
@legacy_router.post("/sync/query", response_model=QueryResponse)
def sync_query_endpoint(request_body: QueryRequest, http_request: Request):
    """
    SYNCHRONOUS BASELINE ENDPOINT FOR SCIENTIFIC BENCHMARKING.
    Notice this function is intentionally defined with 'def' (NOT 'async def')
    so that FastAPI executes it in Starlette's threadpool.
    It executes blocking file reads, blocking simulated I/O (time.sleep),
    and synchronous token scoring.
    """
    start_t = time.perf_counter()
    request_id = getattr(http_request.state, "request_id", "sync-direct")

    raw_results = sync_service.query(
        question=request_body.question,
        top_k=request_body.top_k,
        category=request_body.category,
        simulate_io_delay=0.04
    )

    elapsed_ms = round((time.perf_counter() - start_t) * 1000.0, 3)

    return {
        "question": request_body.question,
        "matched_count": len(raw_results),
        "results": [DocumentRecord(**r) for r in raw_results],
        "execution_mode": "sync",
        "duration_ms": elapsed_ms,
        "request_id": request_id
    }
