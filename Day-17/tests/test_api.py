"""
Day 17 — Automated Robustness and Functional Tests
Uses FastAPI TestClient to execute all 10 test cases against the live API.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add Day-17 to sys.path so app can be imported cleanly
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.main import app
from app.rag_service import RAGService

client = TestClient(app)
DOCS_DIR = os.path.join(BASE_DIR, "documents")


@pytest.fixture(scope="session", autouse=True)
def init_clean_service():
    """Ensure clean RAG state before running tests."""
    rag = RAGService.get_instance()
    rag.documents_registry.clear()
    try:
        rag.chroma_client.delete_collection(rag.collection_name)
    except Exception:
        pass
    rag.collection = rag.chroma_client.create_collection(
        name=rag.collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    yield


def test_01_root_endpoint():
    """GET / — Verify root endpoint and service discovery."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "endpoints" in data


def test_02_health_initial():
    """GET /health — Verify initial health check stats."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["documents_indexed"] == 0
    assert data["total_chunks"] == 0


def test_03_ask_before_upload():
    """TEST 7 — POST /ask before any document is uploaded (Expected: 400 Bad Request)."""
    response = client.post("/ask", json={"question": "What is the submission deadline?"})
    assert response.status_code == 400
    data = response.json()
    assert "No documents have been uploaded yet" in data["detail"]


def test_04_upload_unsupported_file():
    """TEST 4 — POST /upload with unsupported format (Expected: 415 Unsupported Media Type)."""
    jpg_path = os.path.join(DOCS_DIR, "image_file.jpg")
    with open(jpg_path, "rb") as f:
        response = client.post("/upload", files={"file": ("image_file.jpg", f, "image/jpeg")})
    assert response.status_code == 415
    data = response.json()
    assert "Unsupported file format '.jpg'" in data["detail"]


def test_05_upload_empty_file():
    """TEST 3 — POST /upload with 0-byte file (Expected: 400 Bad Request)."""
    empty_path = os.path.join(DOCS_DIR, "empty.pdf")
    with open(empty_path, "rb") as f:
        response = client.post("/upload", files={"file": ("empty.pdf", f, "application/pdf")})
    assert response.status_code == 400
    data = response.json()
    assert "empty (0 bytes)" in data["detail"]


def test_06_upload_corrupted_pdf():
    """TEST 5 — POST /upload with corrupted PDF binary (Expected: 400 Bad Request)."""
    corrupt_path = os.path.join(DOCS_DIR, "corrupted.pdf")
    with open(corrupt_path, "rb") as f:
        response = client.post("/upload", files={"file": ("corrupted.pdf", f, "application/pdf")})
    assert response.status_code == 400
    data = response.json()
    assert "Invalid or corrupted PDF file" in data["detail"]


def test_07_upload_normal_pdf():
    """TEST 1 — POST /upload with valid multi-page PDF (Expected: 200 OK)."""
    pdf_path = os.path.join(DOCS_DIR, "sample_onboarding.pdf")
    with open(pdf_path, "rb") as f:
        response = client.post("/upload", files={"file": ("sample_onboarding.pdf", f, "application/pdf")})
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "sample_onboarding.pdf"
    assert data["pages_count"] == 2
    assert data["chunks_count"] > 0
    assert "document_id" in data


def test_08_upload_valid_txt():
    """TEST 2 — POST /upload with valid text document (Expected: 200 OK)."""
    txt_path = os.path.join(DOCS_DIR, "sample_policy.txt")
    with open(txt_path, "rb") as f:
        response = client.post("/upload", files={"file": ("sample_policy.txt", f, "text/plain")})
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "sample_policy.txt"
    assert data["chunks_count"] > 0


def test_09_list_documents():
    """GET /documents — Verify indexed documents are properly listed."""
    response = client.get("/documents")
    assert response.status_code == 200
    data = response.json()
    assert data["total_documents"] == 2
    filenames = [d["filename"] for d in data["documents"]]
    assert "sample_onboarding.pdf" in filenames
    assert "sample_policy.txt" in filenames


def test_10_empty_question():
    """TEST 8 — POST /ask with empty/blank query (Expected: 400 or 422)."""
    response = client.post("/ask", json={"question": "   "})
    assert response.status_code in [400, 422]


def test_11_normal_question():
    """TEST 9 — POST /ask with valid question (Expected: 200 OK with answer and sources)."""
    response = client.post("/ask", json={"question": "What is the daily task submission deadline?", "top_k": 2})
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "What is the daily task submission deadline?"
    assert len(data["answer"]) > 0
    assert data["total_sources"] > 0
    source = data["sources"][0]
    assert "filename" in source
    assert "page_number" in source
    assert "similarity_score" in source
    assert "text_snippet" in source


def test_12_upload_large_document():
    """TEST 6 — POST /upload with large multi-page PDF within 10MB limit (Expected: 200 OK)."""
    large_path = os.path.join(DOCS_DIR, "large_document.pdf")
    with open(large_path, "rb") as f:
        response = client.post("/upload", files={"file": ("large_document.pdf", f, "application/pdf")})
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "large_document.pdf"
    assert data["chunks_count"] > 10


def test_13_document_deletion():
    """TEST 10 (Additional Functional Test) — DELETE /documents/{doc_id}."""
    # List documents to get an ID
    list_res = client.get("/documents")
    docs = list_res.json()["documents"]
    assert len(docs) > 0
    doc_to_delete = docs[0]
    doc_id = doc_to_delete["document_id"]

    del_res = client.delete(f"/documents/{doc_id}")
    assert del_res.status_code == 200
    del_data = del_res.json()
    assert del_data["document_id"] == doc_id
    assert del_data["chunks_removed"] > 0

    # Verify document is gone from registry
    list_res2 = client.get("/documents")
    remaining_ids = [d["document_id"] for d in list_res2.json()["documents"]]
    assert doc_id not in remaining_ids


def test_14_upload_oversized_file():
    """Verify 10 MB payload ceiling (Expected: 413 Payload Too Large)."""
    over_path = os.path.join(DOCS_DIR, "oversized_document.pdf")
    with open(over_path, "rb") as f:
        response = client.post("/upload", files={"file": ("oversized_document.pdf", f, "application/pdf")})
    assert response.status_code == 413
    data = response.json()
    assert "exceeds maximum allowed limit of 10 MB" in data["detail"]

