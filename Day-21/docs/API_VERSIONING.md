# Day 21 — API Versioning & Backward Compatibility

## 1. Enterprise Versioning Strategy

As an API evolves to support new features (such as asynchronous batch querying and audit telemetry), existing client integrations and front-end mobile apps must not break.

Day 21 implements **URI Path Versioning** (`/api/v1`) while explicitly maintaining **Legacy Compatibility Routes** that preserve the original endpoints developed in Day 17.

```
Incoming Request
      │
      ├── Path starts with /api/v1/... ──► [v1 Router (Asynchronous, Protected, Enhanced)]
      │                                       - GET /api/v1/health
      │                                       - POST /api/v1/query
      │                                       - POST /api/v1/batch-query
      │                                       - GET /api/v1/audit/logs
      │                                       - GET /api/v1/metrics
      │
      └── Unversioned Legacy Path ───────► [Legacy Router (Backward Compatible)]
                                              - GET /
                                              - GET /health
                                              - GET /documents
                                              - POST /ask
                                              - POST /sync/query (Baseline Benchmark)
```

---

## 2. Route Compatibility Mapping Table

| Endpoint Path | HTTP Method | Router Category | Target Service / Handler | Compatibility Purpose |
| :--- | :---: | :---: | :--- | :--- |
| `/` | `GET` | Legacy | `legacy_root()` | Root service discovery, welcome payload, endpoint index. |
| `/health` | `GET` | Legacy | `legacy_health()` | Preserves Day-17 health check format. |
| `/documents` | `GET` | Legacy | `legacy_documents()` | Preserves Day-17 document listing contract. |
| `/ask` | `POST` | Legacy | `legacy_ask()` | Preserves Day-17 RAG question-answering contract (`{question, top_k}`). |
| `/sync/query` | `POST` | Baseline | `sync_query_endpoint()` | Synchronous baseline endpoint for scientific performance benchmarking. |
| `/api/v1/health` | `GET` | Version 1 | `v1_health()` | Enhanced health diagnostics with uptime, worker mode, and corpus stats. |
| `/api/v1/query` | `POST` | Version 1 | `v1_query()` | Authenticated, non-blocking asynchronous document search with background audit logging. |
| `/api/v1/batch-query` | `POST` | Version 1 | `v1_batch_query()` | Bounded concurrent batch query execution using `asyncio.gather()` and Semaphore. |
| `/api/v1/audit/logs` | `GET` | Version 1 | `v1_audit_logs()` | Admin-protected paginated audit record inspection. |
| `/api/v1/metrics` | `GET` | Version 1 | `v1_metrics()` | Live middleware latency telemetry and request counters. |

---

## 3. Deprecation and Evolution Roadmap

1. **Phase 1 (Current — Day 21):** Both legacy routes and `/api/v1` routes operate concurrently. Existing Day-17 client integrations work without modification.
2. **Phase 2 (Future Notice):** Legacy routes will include the `Deprecation: true` HTTP response header and `Sunset` date, encouraging clients to migrate to `/api/v1`.
3. **Phase 3 (Major Version Bump):** When breaking schema changes are introduced, a new `/api/v2` router is registered, leaving `/api/v1` intact for existing contracts.
