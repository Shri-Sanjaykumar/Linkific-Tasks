# Day 21 — Asynchronous Programming, Middleware, Background Tasks, Dependency Injection, API Versioning & Performance Optimization

**Linkific AI/ML Internship**  
**Author:** Shri Sanjaykumar V  
**Date:** September 23, 2026  
**Status:** Complete & Fully Verified  

---

## 📖 Overview

Day 21 focuses on transforming synchronous REST APIs into high-throughput, enterprise-ready asynchronous microservices using **FastAPI**, **Starlette ASGI**, and **Python 3.14 async/await primitives**. 

The project converts the synchronous document retrieval pattern introduced in Day 17 into an asynchronous architecture featuring:
1. **Asynchronous I/O & Threadpool Offloading:** Non-blocking file reading (`aiofiles`), cooperative I/O scheduling, and CPU-intensive token scoring offloaded to worker threads via `anyio.to_thread.run_sync`.
2. **Request-Processing Middleware:** Automatic correlation tracking with UUID4 `X-Request-ID`, microsecond-precision timing with `X-Process-Time-Ms`, structured request/response logging, and thread-safe in-memory metrics aggregation.
3. **In-Process Background Tasks:** Decoupled audit logging to JSON Lines (`.jsonl`) via FastAPI `BackgroundTasks`, protected by re-entrant threading locks and isolated error boundaries.
4. **Hierarchical Dependency Injection:** Security verification with constant-time HMAC comparison, role-based authorization (User vs. Admin), context extraction, query pagination, and loose service coupling.
5. **API Versioning & Backward Compatibility:** URL path prefixing (`/api/v1/...`) isolating modern asynchronous endpoints while preserving legacy Day 17 routes (`/`, `/health`, `/documents`, `/ask`, `/sync/query`) with 100% contract parity.
6. **Empirical Performance Benchmarking:** A scientific benchmarking harness measuring latency distributions ($p_{50}, p_{90}, p_{95}$), throughput ($RPS$), and error rates across concurrent and sequential workloads.

---

## 🗂 Project Directory Structure

```
Day-21/
├── app/
│   ├── __init__.py
│   ├── config.py                 # Pydantic BaseSettings, environment configuration
│   ├── schemas.py                # Strict Pydantic v2 data models & validation
│   ├── exceptions.py             # Centralized JSON error envelopes (401, 403, 404, 422, 500)
│   ├── middleware.py             # RequestLoggingMiddleware & in-memory MetricsTracker
│   ├── background_tasks.py       # Thread-safe JSONL audit writer & reader
│   ├── dependencies.py           # FastAPI Depends() security, context, pagination, services
│   ├── main.py                   # FastAPI application factory, lifespan, CORS, routers
│   ├── api/
│   │   ├── __init__.py
│   │   ├── legacy.py             # Backward-compatible Day-17 routes + /sync/query baseline
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints.py      # Modern /api/v1/ asynchronous endpoints
│   └── services/
│       ├── __init__.py
│       ├── sync_service.py       # Synchronous baseline service (blocking file I/O & sleep)
│       └── async_service.py      # Non-blocking async service (aiofiles + threadpool)
├── data/
│   ├── sample_docs.json          # Pre-loaded document corpus for search and scoring
│   └── activity_audit.jsonl      # Append-only background task audit trail
├── docs/
│   ├── ASYNC_PROGRAMMING.md      # Non-blocking I/O, event loop mechanics, coroutines
│   ├── MIDDLEWARE.md             # Pipeline architecture, correlation IDs, telemetry
│   ├── BACKGROUND_TASKS.md       # In-process audit logging, locks, Celery migration path
│   ├── DEPENDENCY_INJECTION.md   # Security gating, pagination, service abstraction, testing overrides
│   ├── API_VERSIONING.md         # URI path versioning, legacy routing, contract evolution
│   ├── PERFORMANCE_BENCHMARK.md  # Formal benchmark report, percentiles, methodology
│   ├── API_DOCUMENTATION.md      # OpenAPI specification, header contracts, error schemas
│   └── TESTING_AND_EXECUTION_REPORT.md # PyTest coverage report, regression test matrix
├── outputs/
│   ├── benchmark_baseline.json   # Raw JSON metrics for synchronous baseline
│   ├── benchmark_async.json      # Raw JSON metrics for asynchronous endpoint
│   ├── benchmark_comparison.json # Comparative statistical analysis & percentiles
│   └── verification_summary.md   # Master verification checklist and objective completion audit
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Shared fixtures, test settings, mock credentials
│   ├── test_schemas.py           # Pydantic contract validation tests
│   ├── test_services.py          # Sync vs async logic parity and scoring tests
│   ├── test_dependencies.py      # Auth, admin, pagination, and context tests
│   ├── test_middleware.py        # Request ID propagation & timing header tests
│   ├── test_background_tasks.py  # JSONL file lock & background task execution tests
│   ├── test_legacy_routes.py     # Day 17 contract backward-compatibility tests
│   ├── test_api_v1.py            # Asynchronous endpoints, audit retrieval & metrics tests
│   ├── test_batch_queries.py     # Bounded batch queries & semaphore concurrency tests
│   └── test_error_handlers.py    # Standardized error envelopes (401, 403, 404, 422, 500)
├── benchmark.py                  # Core benchmarking engine (httpx client & percentiles)
├── requirements.txt              # Production and development dependencies
├── run_benchmark.py              # CLI runner for ASGI & Live Server benchmarks
├── run_server.py                 # Uvicorn entry point script
└── README.md                     # Master project documentation (this file)
```

---

## ⚡ Quickstart Guide

### 1. Environment Setup & Installation
```bash
# Navigate to the Day 21 directory
cd C:\projects\linkific\internship\Day-21

# Install required dependencies
pip install -r requirements.txt
```

### 2. Running the Microservice
```bash
# Start server with default host (127.0.0.1) and port (8000)
python run_server.py

# Or run with custom host and port via Uvicorn
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive API documentation will be available at:
- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`

### 3. Running Automated Tests
```bash
# Run all 44 Day-21 automated tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=app --cov-report=term-missing
```

### 4. Running the Performance Benchmark
```bash
# Run in-process ASGI benchmark
python run_benchmark.py --mode asgi --requests 50 --concurrency 10

# Or run live HTTP server benchmark (automatically boots and tears down a test server on port 8009)
python run_benchmark.py --mode server --port 8009 --requests 50 --concurrency 10
```

---

## 🚀 API Catalog

### Modern Asynchronous Endpoints (`/api/v1`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|:---:|
| `GET` | `/api/v1/health` | Service health status, version, and server timestamp | None |
| `POST` | `/api/v1/query` | Asynchronous single document query with background audit logging | User (`X-API-Key`) |
| `POST` | `/api/v1/batch-query` | Bounded concurrent batch query (up to 10 queries, semaphore=5) | User (`X-API-Key`) |
| `GET` | `/api/v1/audit/logs` | Paginated view of background task audit log records | Admin (`X-API-Key`) |
| `GET` | `/api/v1/metrics` | Real-time in-memory request count, errors, and average latency | Admin (`X-API-Key`) |

### Legacy Backward-Compatible Endpoints

| Method | Endpoint | Description | Auth Required |
|---|---|---|:---:|
| `GET` | `/` | Root endpoint displaying API metadata and available routes | None |
| `GET` | `/health` | Legacy Day 17 health check contract | None |
| `GET` | `/documents` | Lists all pre-loaded knowledge base documents | None |
| `POST` | `/ask` | Legacy Day 17 query endpoint mapping to synchronous service | None |
| `POST` | `/sync/query` | Synchronous baseline endpoint used for comparative benchmarking | User (`X-API-Key`) |

---

## 📊 Performance Benchmark Results

Benchmarked using live HTTP socket transport (`http://127.0.0.1:8009`) under identical hardware, payloads, and concurrency levels ($N=50, C=10$):

| Metric | Synchronous Baseline (`/sync/query`) | Asynchronous Optimized (`/api/v1/query`) | Performance Delta |
|---|:---:|:---:|:---:|
| **Total Wall Time** | 1.1483 s | 0.8902 s | **-22.48% faster** |
| **Throughput (RPS)** | 43.54 req/s | 56.17 req/s | **+29.01% throughput** |
| **Mean Latency** | 208.70 ms | 166.77 ms | **-20.09% lower** |
| **Median ($p_{50}$)** | 141.98 ms | 161.47 ms | +13.73% |
| **90th Percentile ($p_{90}$)** | 465.54 ms | 236.27 ms | **-49.25% lower** |
| **95th Percentile ($p_{95}$)** | 471.10 ms | 253.72 ms | **-46.14% lower** |
| **Maximum Latency** | 492.02 ms | 272.71 ms | **-44.57% lower** |
| **Error Rate** | 0.0% (0/50) | 0.0% (0/50) | Zero errors |

### Key Benchmark Insights
- **Queueing Saturation Eliminated:** In synchronous execution, concurrent HTTP requests saturate worker threads, causing subsequent requests to queue up. This produces massive latency spikes in tail percentiles ($p_{95} = 471.10\text{ ms}$).
- **Event-Loop Efficiency:** By leveraging non-blocking asynchronous I/O (`aiofiles`) and cooperative delay scheduling (`await asyncio.sleep`), worker threads remain unblocked, collapsing tail latency by **46.14%** ($253.72\text{ ms}$).
- **Throughput Scalability:** Concurrency throughput improved from **43.54 req/s to 56.17 req/s (+29.01%)**.

---

## 🔒 Security & Architecture Highlights

1. **Constant-Time Authentication:** API keys are verified using `hmac.compare_digest()` to eliminate timing attack vulnerabilities.
2. **Safe Secrets Management:** All API keys and operational settings are managed through environment variables and Pydantic `BaseSettings`. Zero secrets are hardcoded in application logic.
3. **Decoupled Exception Envelopes:** Custom handlers catch `HTTPException`, `RequestValidationError`, and unexpected unhandled exceptions (`Exception`), converting them into uniform, sanitized JSON responses that prevent internal stack trace leakage.
4. **Thread-Safe Audit Logging:** Background audit records are serialized with explicit mutex locks (`threading.Lock()`) to guarantee zero race conditions or corrupted JSON Lines during concurrent writes.
5. **Bounded Concurrency:** Batch queries are constrained by a strict maximum batch size (10 items) and governed by an `asyncio.Semaphore(5)` to prevent resource exhaustion or denial-of-service conditions.

---

## 📚 Detailed Documentation

For in-depth architectural specifications and implementation details, refer to the individual documentation modules:
- [Async Programming Guide](docs/ASYNC_PROGRAMMING.md)
- [Middleware Architecture](docs/MIDDLEWARE.md)
- [Background Tasks Architecture](docs/BACKGROUND_TASKS.md)
- [Dependency Injection Guide](docs/DEPENDENCY_INJECTION.md)
- [API Versioning Strategy](docs/API_VERSIONING.md)
- [Scientific Performance Benchmark Report](docs/PERFORMANCE_BENCHMARK.md)
- [API Documentation & Contracts](docs/API_DOCUMENTATION.md)
- [Testing & Execution Report](docs/TESTING_AND_EXECUTION_REPORT.md)
- [Verification Summary & Objective Checklist](outputs/verification_summary.md)
