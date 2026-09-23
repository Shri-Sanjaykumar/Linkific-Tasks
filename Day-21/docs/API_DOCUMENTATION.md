# Day 21 — Comprehensive API Documentation & Specification

## 1. Overview & Service Information

- **Service Name:** Linkific Enterprise AI Service (Day 21)
- **Base URL:** `http://127.0.0.1:8000`
- **Interactive Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc Technical Docs:** `http://127.0.0.1:8000/redoc`
- **OpenAPI JSON Schema:** `http://127.0.0.1:8000/openapi.json`

---

## 2. Authentication Specification

Endpoints under `/api/v1/query`, `/api/v1/batch-query`, and `/api/v1/audit/logs` require an API Key supplied via the HTTP header:

```http
X-API-Key: <your-api-key>
```

- In development mode (`LINKIFIC_ENV="development"`), if no keys are configured, a development bypass is permitted.
- In testing and production modes, missing or invalid keys return HTTP 401 Unauthorized.
- Administrative endpoints (`/api/v1/audit/logs`) require the `LINKIFIC_ADMIN_API_KEY` and return HTTP 403 Forbidden if called with a standard key.

---

## 3. Endpoints Catalog & Curl Examples

### 3.1 Service Welcome & Discovery
- **Endpoint:** `GET /`
- **Authentication:** None
- **Example Command:**
  ```bash
  curl -s http://127.0.0.1:8000/
  ```
- **Response (200 OK):**
  ```json
  {
    "message": "Welcome to Linkific Enterprise AI Service — Day 21 (Async & Modular Architecture)",
    "status": "online",
    "docs_url": "/docs",
    "version": "1.0.0",
    "endpoints": { ... }
  }
  ```

---

### 3.2 Enhanced System Health
- **Endpoint:** `GET /api/v1/health`
- **Authentication:** None
- **Example Command:**
  ```bash
  curl -s http://127.0.0.1:8000/api/v1/health
  ```
- **Response (200 OK):**
  ```json
  {
    "status": "healthy",
    "uptime_seconds": 45.2,
    "version": "1.0.0",
    "environment": "development",
    "worker_mode": "asynchronous_event_loop",
    "total_indexed_documents": 5
  }
  ```

---

### 3.3 Asynchronous Document Query (Core Endpoint)
- **Endpoint:** `POST /api/v1/query`
- **Authentication:** `X-API-Key: <standard-or-admin-key>`
- **Example Command:**
  ```bash
  curl -X POST http://127.0.0.1:8000/api/v1/query \
    -H "Content-Type: application/json" \
    -H "X-API-Key: test-standard-api-key" \
    -H "X-Request-ID: my-trace-101" \
    -d '{"question": "What is the corporate leave policy?", "top_k": 2}'
  ```
- **Response Headers:**
  ```http
  X-Request-ID: my-trace-101
  X-Process-Time-Ms: 44.821
  ```
- **Response (200 OK):**
  ```json
  {
    "question": "What is the corporate leave policy?",
    "matched_count": 1,
    "results": [
      {
        "id": "DOC-POL-001",
        "title": "Corporate Leave and Attendance Policy",
        "category": "Human Resources",
        "content": "All Linkific employees and interns are entitled to 1.5 paid leave days per completed calendar month...",
        "author": "HR Operations",
        "version": "2.4",
        "word_count": 56,
        "score": 0.8
      }
    ],
    "execution_mode": "async",
    "duration_ms": 44.821,
    "request_id": "my-trace-101"
  }
  ```

---

### 3.4 Concurrent Batch Query
- **Endpoint:** `POST /api/v1/batch-query`
- **Authentication:** `X-API-Key: <standard-or-admin-key>`
- **Constraints:** Maximum 10 queries per request.
- **Example Command:**
  ```bash
  curl -X POST http://127.0.0.1:8000/api/v1/batch-query \
    -H "Content-Type: application/json" \
    -H "X-API-Key: test-standard-api-key" \
    -d '{
      "queries": [
        {"question": "leave policy rules"},
        {"question": "remote hardware security guidelines"}
      ]
    }'
  ```
- **Response (200 OK):**
  ```json
  {
    "total_queries": 2,
    "successful_queries": 2,
    "failed_queries": 0,
    "results": [
      {
        "index": 0,
        "status": "success",
        "result": { "question": "leave policy rules", "matched_count": 1, ... },
        "error": null
      },
      {
        "index": 1,
        "status": "success",
        "result": { "question": "remote hardware security guidelines", "matched_count": 1, ... },
        "error": null
      }
    ],
    "total_duration_ms": 46.12,
    "request_id": "..."
  }
  ```

---

### 3.5 Background Audit Logs (Admin Only)
- **Endpoint:** `GET /api/v1/audit/logs?skip=0&limit=10&order_by=timestamp`
- **Authentication:** `X-API-Key: <admin-key>`
- **Example Command:**
  ```bash
  curl -s http://127.0.0.1:8000/api/v1/audit/logs?skip=0&limit=5 \
    -H "X-API-Key: test-admin-api-key"
  ```
- **Response (200 OK):**
  ```json
  {
    "total_records": 12,
    "returned_records": 5,
    "skip": 0,
    "limit": 5,
    "records": [
      {
        "timestamp": "2026-09-23T11:31:26.123456Z",
        "request_id": "my-trace-101",
        "event": "query_completed",
        "endpoint": "/api/v1/query",
        "status": "success",
        "duration_ms": 44.821,
        "client_ip": "127.0.0.1",
        "metadata": { ... }
      }
    ]
  }
  ```

---

### 3.6 Live Middleware Telemetry & Metrics
- **Endpoint:** `GET /api/v1/metrics`
- **Authentication:** None
- **Example Command:**
  ```bash
  curl -s http://127.0.0.1:8000/api/v1/metrics
  ```
- **Response (200 OK):**
  ```json
  {
    "total_requests_processed": 54,
    "average_process_time_ms": 48.21,
    "p95_process_time_ms": 112.5,
    "uptime_seconds": 120.4,
    "active_worker_threads": 4
  }
  ```

---

### 3.7 Synchronous Baseline Query (Benchmark Counterpart)
- **Endpoint:** `POST /sync/query`
- **Authentication:** None / Optional
- **Purpose:** Used directly for fair scientific comparison against `/api/v1/query`.
- **Example Command:**
  ```bash
  curl -X POST http://127.0.0.1:8000/sync/query \
    -H "Content-Type: application/json" \
    -d '{"question": "leave policy rules", "top_k": 2}'
  ```

---

## 4. Standard Error Envelopes

Every error (whether generated by Pydantic validation, missing credentials, route missing, or internal failure) conforms to a uniform schema:

### 4.1 Authentication Error (401 Unauthorized)
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Missing required API key in 'X-API-Key' header.",
    "request_id": "8f89c629-8735-4309-8d76-efd37805d7f1"
  }
}
```

### 4.2 Validation Error (422 Unprocessable Entity)
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request body or query parameter validation failed.",
    "request_id": "8f89c629-8735-4309-8d76-efd37805d7f1",
    "details": [
      {
        "field": "top_k",
        "message": "Input should be greater than or equal to 1",
        "type": "greater_than_equal"
      }
    ]
  }
}
```

### 4.3 General Server Error (500 Internal Server Error)
```json
{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "An unexpected internal server error occurred. Please contact support with the request ID.",
    "request_id": "8f89c629-8735-4309-8d76-efd37805d7f1"
  }
}
```
