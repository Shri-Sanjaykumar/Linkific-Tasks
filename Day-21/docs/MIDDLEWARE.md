# Day 21 — Middleware Architecture & Telemetry

## 1. Architectural Overview

Middleware in FastAPI wraps every incoming HTTP request and its outgoing HTTP response. It executes before route matching, dependency resolution, or endpoint execution, and runs again as the response streams back to the client.

```
Incoming Request
      │
      ▼
[RequestLoggingMiddleware: START]
  - Validate or generate X-Request-ID (UUID4)
  - Record start_time = time.perf_counter()
  - Bind context to request.state
      │
      ▼
[Framework Routing & Dependency Resolution]
      │
      ▼
[Endpoint Execution (e.g. POST /api/v1/query)]
      │
      ▼
[Framework Exception Handlers / Response Serialization]
      │
      ▼
[RequestLoggingMiddleware: COMPLETION]
  - Calculate elapsed_ms = (perf_counter() - start_time) * 1000
  - Record metrics into MetricsTracker
  - Inject headers:
      X-Request-ID: <uuid>
      X-Process-Time-Ms: <float>
      │
      ▼
HTTP Response Returned to Client
      │
      ▼
(FastAPI BackgroundTasks execute in-process)
```

---

## 2. Decoupled Responsibilities: Middleware vs Exception Handlers

Following enterprise software architecture principles, error handling is strictly decoupled from request-processing middleware:

| Layer | Responsibility | Components |
| :--- | :--- | :--- |
| **Request Middleware** | Injects correlation ID, tracks high-precision execution latency, injects telemetry headers, logs request start and finish. | `RequestLoggingMiddleware` in `app/middleware.py` |
| **Framework HTTP Exception Handler** | Maps client errors (400, 401, 403, 404) to standard JSON error envelopes without exposing stack traces. | `http_exception_handler` in `app/exceptions.py` |
| **Validation Exception Handler** | Formats Pydantic parameter/body validation errors (422) with granular field paths. | `validation_exception_handler` in `app/exceptions.py` |
| **General Catch-All Exception Handler** | Intercepts unexpected server crashes (500), logs full tracebacks to server-side stderr with the correlation ID, and returns a safe error message to the client. | `general_exception_handler` in `app/exceptions.py` |

---

## 3. Correlation ID (`X-Request-ID`) Policy

Every request must be traceable across distributed microservices, application logs, and audit records.

1. **Client-Provided IDs:** If the incoming HTTP request contains an `X-Request-ID` header matching the safe regex `^[a-zA-Z0-9_\-]{1,64}$`, the application preserves it.
2. **Missing or Malformed IDs:** If the header is missing, exceeds 64 characters, or contains invalid characters, the middleware generates a new RFC 4122 `uuid.uuid4()`.
3. **Propagation:** The ID is stored in `request.state.request_id` and attached to:
   - Response header `X-Request-ID`
   - Server stdout/stderr logs: `[<request_id>] COMPLETED POST /api/v1/query Status=200`
   - Background audit log records in `data/activity_audit.jsonl`
   - All error response envelopes (`{"error": {"request_id": "<uuid>", ...}}`)

---

## 4. Latency Timing Header (`X-Process-Time-Ms`)

- **Format:** Single unambiguous numeric millisecond float: `X-Process-Time-Ms: 12.435`
- **Precision:** Measured using `time.perf_counter()`, which provides the highest available resolution monotonic clock on the OS.
- **Timing Boundary:** Measures the complete HTTP request lifecycle: middleware entry -> routing -> dependency injection -> endpoint coroutine -> response serialization -> middleware exit.
- **Background Task Isolation:** FastAPI `BackgroundTasks` execute *after* response headers are sent; hence, background file writes do not inflate `X-Process-Time-Ms`.
