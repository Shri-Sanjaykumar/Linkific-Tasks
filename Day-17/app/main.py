"""
Day 17 — Production-Grade FastAPI RAG Application
Exposes modular RAG capabilities over HTTP with strict error handling, Swagger UI,
file upload, page-aware text extraction, semantic retrieval, and T5 answer generation.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from .schemas import (
    WelcomeResponse,
    HealthResponse,
    UploadResponse,
    DocumentListResponse,
    DeleteDocumentResponse,
    QuestionRequest,
    AnswerResponse
)
from .document_processor import DocumentProcessingError, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP
from .rag_service import RAGService


app = FastAPI(
    title="Linkific RAG API",
    description="""
**Linkific AI/ML Internship — Day 17: FastAPI-Powered Retrieval-Augmented Generation (RAG)**

This API extends the Day 16 RAG architecture into a modular, production-ready microservice.
Key capabilities include:
- **Document Ingestion:** Multi-page PDF (page-aware) and TXT file uploads (up to 10 MB).
- **Chunking & Vector Storage:** Configurable sliding-window chunking (default 800 chars) with ChromaDB indexing.
- **Dense Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` generating 384-dimensional normalized vectors.
- **Semantic Search & Generation:** Cosine similarity retrieval + local Hugging Face `google-t5/t5-small` answer generation.
- **Document Management:** Document registry tracking and deletion capabilities.
- **Robust Error Handling:** Strict HTTP status mapping (400, 404, 413, 415, 422, 500) without raw stack traces.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# ------------------------------------------------------------------------------
# Exception Handlers
# ------------------------------------------------------------------------------
@app.exception_handler(DocumentProcessingError)
async def document_processing_exception_handler(request, exc: DocumentProcessingError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc), "status_code": exc.status_code}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err.get("loc", []))
        errors.append(f"{field}: {err.get('msg')}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Request validation failed: " + "; ".join(errors),
            "status_code": 422
        }
    )


# ------------------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------------------
@app.get("/", response_model=WelcomeResponse, tags=["General"])
async def root():
    """Welcome endpoint with API discovery and status."""
    return {
        "message": "Welcome to Linkific RAG API — Day 17 Internship Project",
        "status": "online",
        "docs_url": "/docs",
        "endpoints": {
            "GET /": "API Welcome and metadata",
            "GET /health": "System health and index statistics",
            "POST /upload": "Upload and index a PDF or TXT document (multipart/form-data)",
            "GET /documents": "List all currently indexed documents",
            "DELETE /documents/{document_id}": "Delete document and remove its chunks",
            "POST /ask": "Ask a question and receive context-grounded AI answer"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Operational health check and vector database stats."""
    rag_service = RAGService.get_instance()
    stats = rag_service.get_health_stats()
    return stats


@app.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_200_OK,
    tags=["Document Ingestion"],
    responses={
        400: {"description": "Empty file or invalid content"},
        413: {"description": "File exceeds 10 MB limit"},
        415: {"description": "Unsupported file format (only PDF and TXT allowed)"}
    }
)
async def upload_document(
    file: UploadFile = File(..., description="PDF or TXT document to process and index"),
    chunk_size: int = Query(default=DEFAULT_CHUNK_SIZE, ge=100, le=2000, description="Chunk size in characters (default 800)"),
    overlap: int = Query(default=DEFAULT_CHUNK_OVERLAP, ge=0, le=500, description="Overlap between consecutive chunks in characters (default 100)")
):
    """
    Upload and process a document:
    1. Validates file extension and size (<= 10MB).
    2. Extracts text (page-by-page for PDF).
    3. Splits text into overlapping chunks.
    4. Generates dense 384-dimensional embeddings.
    5. Stores chunks and metadata in ChromaDB.
    """
    rag_service = RAGService.get_instance()

    filename = file.filename or "uploaded_document"
    try:
        content = await file.read()
    except Exception as e:
        raise DocumentProcessingError(f"Failed to read uploaded file: {str(e)}", status_code=400)

    # Process and index
    result = rag_service.process_and_index_document(
        filename=filename,
        file_bytes=content,
        chunk_size=chunk_size,
        overlap=overlap
    )
    return result


@app.get("/documents", response_model=DocumentListResponse, tags=["Document Management"])
async def list_documents():
    """List all currently indexed documents with metadata."""
    rag_service = RAGService.get_instance()
    docs = rag_service.list_documents()
    return {
        "total_documents": len(docs),
        "documents": docs
    }


@app.delete(
    "/documents/{document_id}",
    response_model=DeleteDocumentResponse,
    tags=["Document Management"],
    responses={
        404: {"description": "Document ID not found"}
    }
)
async def delete_document(document_id: str):
    """Remove an indexed document and its associated chunks from ChromaDB."""
    rag_service = RAGService.get_instance()
    result = rag_service.delete_document(document_id)
    return result


@app.post(
    "/ask",
    response_model=AnswerResponse,
    tags=["RAG Question Answering"],
    responses={
        400: {"description": "No documents uploaded or invalid question"}
    }
)
async def ask_question(request: QuestionRequest):
    """
    Ask a question over the indexed documents:
    1. Validates query.
    2. Generates query embedding.
    3. Retrieves top-k chunks from ChromaDB.
    4. Constructs grounded prompt.
    5. Synthesizes answer using local T5 Seq2Seq model.
    6. Returns answer with source file names, page numbers, and cosine similarity scores.
    """
    rag_service = RAGService.get_instance()
    result = rag_service.ask_question(
        question=request.question,
        top_k=request.top_k or 2
    )
    return result
