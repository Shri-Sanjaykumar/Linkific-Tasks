# Day 17 — FastAPI-Based RAG Microservice Testing Report

**Project:** Linkific AI/ML Internship — Month 1 Training  
**Intern:** Shri Sanjaykumar V  
**Date:** 18 September 2026  
**Execution Environment:** Python 3.13.12, FastAPI 0.141.1, Uvicorn 0.53.0, ChromaDB 1.5.9, Sentence-Transformers 6.0.1, PyTorch 2.13.0, PyTest 9.1.1  
**API Protocol:** HTTP REST via ASGI TestClient / Uvicorn (Port 8000)  

---

## 1. Executive Testing Summary

The test suite for the **FastAPI-based RAG microservice** is implemented in `tests/test_api.py` and contains **14 automated test functions**. These tests are organized into three distinct verification tiers:

1. **Endpoint Smoke Tests (3 tests):** Validates basic HTTP availability, service discovery, root payload schema, health statistics, and document listing.
2. **Robustness Tests (7 tests):** Validates defensive error handling against malformed inputs, unsupported formats, zero-byte uploads, corrupted binary streams, blank queries, out-of-order execution, 2.05 MB large document ingestion, and 10 MB payload ceiling enforcement.
3. **Core Functional Tests (4 tests):** Validates end-to-end RAG workflows: multi-page PDF text extraction, plain text ingestion, semantic search with local T5-small answer generation, and document/vector deletion.

**Overall Automated Test Suite Results (`pytest tests/test_api.py -v`):**
- **Total Test Functions:** 14
- **Passed:** 14
- **Failed:** 0
- **Pass Rate:** **100.0%**
- **Total Execution Duration:** 56.81 seconds

---

## 2. Comprehensive Test Taxonomy (14 Automated PyTest Tests)

| Category | Test Function | Target Endpoint | Input Scenario | Expected Status | Actual Status | Result |
| :--- | :--- | :---: | :--- | :---: | :---: | :---: |
| **Endpoint Smoke** | `test_01_root_endpoint` | `GET /` | Service discovery and endpoint catalog | 200 | **200** | **PASS** |
| **Endpoint Smoke** | `test_02_health_initial` | `GET /health` | Initial operational status & 0 indexed documents | 200 | **200** | **PASS** |
| **Robustness** | `test_03_ask_before_upload` | `POST /ask` | Valid question asked before any document upload | 400 | **400** | **PASS** |
| **Robustness** | `test_04_upload_unsupported_file` | `POST /upload` | Binary image payload (`image_file.jpg`) | 415 | **415** | **PASS** |
| **Robustness** | `test_05_upload_empty_file` | `POST /upload` | Zero-byte payload (`empty.pdf`) | 400 | **400** | **PASS** |
| **Robustness** | `test_06_upload_corrupted_pdf` | `POST /upload` | Malformed stream lacking PDF trailer/xref | 400 | **400** | **PASS** |
| **Functional** | `test_07_upload_normal_pdf` | `POST /upload` | Valid 2-page PDF (`sample_onboarding.pdf`) | 200 | **200** | **PASS** |
| **Functional** | `test_08_upload_valid_txt` | `POST /upload` | Valid plain text file (`sample_policy.txt`) | 200 | **200** | **PASS** |
| **Endpoint Smoke** | `test_09_list_documents` | `GET /documents` | Verification of indexed document registry | 200 | **200** | **PASS** |
| **Robustness** | `test_10_empty_question` | `POST /ask` | Whitespace-only query (`"   "`) | 400 | **400** | **PASS** |
| **Functional** | `test_11_normal_question` | `POST /ask` | "What is the daily task submission deadline?" | 200 | **200** | **PASS** |
| **Robustness** | `test_12_upload_large_document` | `POST /upload` | 14-page synthetic PDF (`large_document.pdf`, 2.05 MB) | 200 | **200** | **PASS** |
| **Functional** | `test_13_document_deletion` | `DELETE /documents/{id}` | Purge document ID and associated vectors | 200 | **200** | **PASS** |
| **Robustness** | `test_14_upload_oversized_file` | `POST /upload` | Oversized PDF (`oversized_document.pdf`, 14.47 MB) | 413 | **413** | **PASS** |

---

## 3. Actual Observed Latencies & Payloads (Live Benchmark Execution)

The table below records actual execution latencies and responses captured during the live benchmark run (`run_and_report_robustness.py`):

| Test ID | Scenario Description | Category | Method & Endpoint | Payload / Input | Expected Status | Actual Status | Execution Latency | Result |
| :---: | :--- | :---: | :---: | :--- | :---: | :---: | :---: | :---: |
| **T1** | Question Before Upload | Robustness | `POST /ask` | Query before document indexing | 400 | **400** | 17.95 ms | **PASS** |
| **T2** | Unsupported File Format | Robustness | `POST /upload` | Image file (`image_file.jpg`) | 415 | **415** | 4.84 ms | **PASS** |
| **T3** | Empty File | Robustness | `POST /upload` | 0-byte file (`empty.pdf`) | 400 | **400** | 5.44 ms | **PASS** |
| **T4** | Corrupted PDF | Robustness | `POST /upload` | Malformed stream (`corrupted.pdf`) | 400 | **400** | 4.31 ms | **PASS** |
| **T5** | Normal PDF Ingestion | Functional | `POST /upload` | 2-page PDF (`sample_onboarding.pdf`) | 200 | **200** | 304.43 ms | **PASS** |
| **T6** | Valid TXT Ingestion | Functional | `POST /upload` | Plain text (`sample_policy.txt`) | 200 | **200** | 162.07 ms | **PASS** |
| **T7** | Large PDF Processing | Robustness | `POST /upload` | 14-page PDF (`large_document.pdf`, 2.05 MB) | 200 | **200** | 1064.07 ms | **PASS** |
| **T8** | Empty Question | Robustness | `POST /ask` | Whitespace query (`"   "`) | 400 | **400** | 3.95 ms | **PASS** |
| **T9** | Normal RAG Question | Functional | `POST /ask` | "What is the daily task submission deadline?" | 200 | **200** | 302.83 ms | **PASS** |
| **T10** | Document Deletion | Functional | `DELETE /documents/{id}` | Purge document ID and vectors | 200 | **200** | 12.72 ms | **PASS** |
| **T11** | Oversized File Limit | Robustness | `POST /upload` | 14.47 MB PDF (`oversized_document.pdf`) | 413 | **413** | 134.60 ms | **PASS** |

---

## 4. Detailed Per-Scenario Response Payloads

### T1: Question Before Upload (Robustness)
- **Endpoint:** `POST /ask`
- **Actual Status:** `400 Bad Request` | **Latency:** `17.95 ms`
```json
{
  "detail": "No documents have been uploaded yet. Please upload a document before asking questions.",
  "status_code": 400
}
```

### T2: Unsupported File Format (Robustness)
- **Endpoint:** `POST /upload`
- **Actual Status:** `415 Unsupported Media Type` | **Latency:** `4.84 ms`
```json
{
  "detail": "Unsupported file format '.jpg'. Supported formats are: .pdf, .txt",
  "status_code": 415
}
```

### T3: Empty File Upload (Robustness)
- **Endpoint:** `POST /upload`
- **Actual Status:** `400 Bad Request` | **Latency:** `5.44 ms`
```json
{
  "detail": "Uploaded file is empty (0 bytes).",
  "status_code": 400
}
```

### T4: Corrupted PDF Upload (Robustness)
- **Endpoint:** `POST /upload`
- **Actual Status:** `400 Bad Request` | **Latency:** `4.31 ms`
```json
{
  "detail": "Invalid or corrupted PDF file: Stream has ended unexpectedly",
  "status_code": 400
}
```

### T5: Normal PDF Ingestion (Functional)
- **Endpoint:** `POST /upload`
- **Actual Status:** `200 OK` | **Latency:** `304.43 ms`
```json
{
  "document_id": "99d93505",
  "filename": "sample_onboarding.pdf",
  "file_type": ".pdf",
  "file_size_bytes": 3488,
  "pages_count": 2,
  "chunks_count": 4,
  "chunk_size": 800,
  "overlap": 100,
  "message": "Document 'sample_onboarding.pdf' successfully processed and indexed (4 chunks created)."
}
```

### T6: Valid TXT Ingestion (Functional)
- **Endpoint:** `POST /upload`
- **Actual Status:** `200 OK` | **Latency:** `162.07 ms`
```json
{
  "document_id": "87c4fae1",
  "filename": "sample_policy.txt",
  "file_type": ".txt",
  "file_size_bytes": 1133,
  "pages_count": 1,
  "chunks_count": 2,
  "chunk_size": 800,
  "overlap": 100,
  "message": "Document 'sample_policy.txt' successfully processed and indexed (2 chunks created)."
}
```

### T7: Large PDF Document Ingestion (Robustness)
- **Endpoint:** `POST /upload`
- **Actual Status:** `200 OK` | **Latency:** `1064.07 ms`
```json
{
  "document_id": "e686eeef",
  "filename": "large_document.pdf",
  "file_type": ".pdf",
  "file_size_bytes": 2050948,
  "pages_count": 14,
  "chunks_count": 28,
  "chunk_size": 800,
  "overlap": 100,
  "message": "Document 'large_document.pdf' successfully processed and indexed (28 chunks created)."
}
```

### T8: Empty / Blank Question (Robustness)
- **Endpoint:** `POST /ask`
- **Actual Status:** `400 Bad Request` | **Latency:** `3.95 ms`
```json
{
  "detail": "Question must contain at least 3 non-whitespace characters.",
  "status_code": 400
}
```

### T9: Normal RAG Question Answering (Functional)
- **Endpoint:** `POST /ask`
- **Actual Status:** `200 OK` | **Latency:** `302.83 ms`
```json
{
  "question": "What is the daily task submission deadline?",
  "answer": "6:00 PM IST",
  "total_sources": 2,
  "sources": [
    {
      "document_id": "99d93505",
      "filename": "sample_onboarding.pdf",
      "page_number": 2,
      "chunk_id": 2,
      "similarity_score": 0.4498,
      "cosine_distance": 0.5502,
      "text_snippet": "Section 3: Task Submission Guidelines\nAll daily technical tasks must be completed and submitted by 6:00 PM IST each evening. Deliverables must be submitted..."
    }
  ]
}
```

### T10: Document Deletion (Functional)
- **Endpoint:** `DELETE /documents/99d93505`
- **Actual Status:** `200 OK` | **Latency:** `12.72 ms`
```json
{
  "document_id": "99d93505",
  "filename": "sample_onboarding.pdf",
  "chunks_removed": 4,
  "message": "Document 'sample_onboarding.pdf' and 4 indexed chunks were successfully removed."
}
```

### T11: Oversized Upload Limit Enforcement (Robustness)
- **Endpoint:** `POST /upload`
- **Actual Status:** `413 Payload Too Large` | **Latency:** `134.60 ms`
```json
{
  "detail": "File size (14.47 MB) exceeds maximum allowed limit of 10 MB.",
  "status_code": 413
}
```

---

## 5. Testing Methodology

1. **Clean Baseline State:** Prior to each test run, ChromaDB collections and the in-memory document registry are cleared to eliminate state pollution.
2. **Realistic Boundary Payloads:**
   - `empty.pdf`: 0-byte file verifying size guards.
   - `corrupted.pdf`: Header followed by malformed bytes without xref/trailer table.
   - `image_file.jpg`: JPEG binary verifying whitelist enforcement.
   - `large_document.pdf`: 2.05 MB, 14-page synthetic technical handbook verifying ingestion scalability.
   - `oversized_document.pdf`: 14.47 MB payload verifying 10 MB ceiling rejection.
3. **Out-of-Order Lifecycle Validation:** Verified that querying `/ask` prior to document upload returns a descriptive 400 error.
4. **Source Attribution & Grounding:** Verified that responses cite accurate `document_id`, `filename`, `page_number`, and cosine similarity scores.

---

## 6. Observed Limitations & Production Roadmap

1. **In-Memory ChromaDB:** The current ChromaDB client runs in-memory; restart resets indexed collections.
2. **Text-Only Extraction:** `pypdf` extracts digital font streams; scanned image PDFs return empty text.
3. **CPU Generator Throughput:** `google-t5/t5-small` inference executes on CPU (~300 ms per query).
4. **Stateless Dialogues:** Single-turn question answering without multi-turn conversation caching.

**Suggested Future Improvements:**
- Persistent vector storage (DuckDB/SQLite mode or client-server ChromaDB/Qdrant).
- OCR fallback pipeline via Tesseract or Google Cloud Document AI.
- Background asynchronous task queue (Celery/Redis) for documents > 5 MB.
- API key authentication (`X-API-Key`) with SlowAPI rate limiting.
- Cross-encoder reranking layer before generation.
