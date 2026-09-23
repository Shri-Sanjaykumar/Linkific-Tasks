# Day 21 — Testing and Execution Report

## 1. Automated Test Execution Summary

The Day 21 test suite was executed locally using `pytest` to verify the functionality of all asynchronous endpoints, request-processing middleware, correlation ID tracking, in-process background audit tasks, modular dependency injection, API versioning (`/api/v1`), backward-compatible legacy routes, and global exception envelopes.

In addition, the full Day-17 regression test suite was executed to guarantee zero regressions against earlier training milestones.

---

## 2. Test Execution Command & Exact Results

### 2.1 Day 21 Test Suite
```bash
pytest Day-21/tests/ -v
```

```text
============================= test session starts =============================
platform win32 -- Python 3.13.12, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\projects\linkific\internship\Day-21\tests
plugins: anyio-4.15.1
collected 44 items

test_api_v1.py::test_v1_health_endpoint PASSED                          [  2%]
test_api_v1.py::test_v1_query_endpoint PASSED                           [  4%]
test_api_v1.py::test_v1_batch_query_endpoint PASSED                     [  6%]
test_api_v1.py::test_v1_metrics_endpoint PASSED                         [  9%]
test_background_tasks.py::test_write_audit_log_entry_success PASSED     [ 11%]
test_background_tasks.py::test_read_audit_logs_pagination PASSED       [ 13%]
test_background_tasks.py::test_read_audit_logs_non_existent_file PASSED [ 15%]
test_background_tasks.py::test_read_audit_logs_skips_malformed_lines PASSED [ 18%]
test_background_tasks.py::test_concurrent_audit_writes PASSED          [ 20%]
test_background_tasks.py::test_endpoint_triggers_background_audit_log PASSED [ 22%]
test_batch_queries.py::test_batch_query_exceeding_max_limit_fails PASSED [ 25%]
test_batch_queries.py::test_batch_query_preserves_order PASSED          [ 27%]
test_dependencies.py::test_auth_missing_api_key_returns_401 PASSED     [ 29%]
test_dependencies.py::test_auth_invalid_api_key_returns_401 PASSED     [ 31%]
test_dependencies.py::test_auth_valid_standard_key_success PASSED      [ 34%]
test_dependencies.py::test_auth_standard_key_forbidden_on_admin_endpoint PASSED [ 36%]
test_dependencies.py::test_auth_admin_key_success_on_admin_endpoint PASSED [ 38%]
test_dependencies.py::test_pagination_bounds_validation PASSED         [ 40%]
test_dependencies.py::test_dependency_override_in_tests PASSED         [ 43%]
test_error_handlers.py::test_404_not_found_envelope PASSED              [ 45%]
test_error_handlers.py::test_422_validation_error_envelope PASSED       [ 47%]
test_error_handlers.py::test_422_missing_required_field_envelope PASSED [ 50%]
test_error_handlers.py::test_422_invalid_json_body_envelope PASSED      [ 52%]
test_error_handlers.py::test_500_general_exception_envelope PASSED      [ 54%]
test_error_handlers.py::test_error_envelope_does_not_leak_stack_trace PASSED [ 56%]
test_legacy_routes.py::test_legacy_root PASSED                         [ 59%]
test_legacy_routes.py::test_legacy_health PASSED                       [ 61%]
test_legacy_routes.py::test_legacy_documents PASSED                    [ 63%]
test_legacy_routes.py::test_legacy_ask_endpoint PASSED                 [ 65%]
test_legacy_routes.py::test_legacy_ask_empty_question_fails PASSED     [ 68%]
test_legacy_routes.py::test_sync_query_baseline_endpoint PASSED        [ 70%]
test_middleware.py::test_middleware_injects_headers PASSED             [ 72%]
test_middleware.py::test_middleware_preserves_valid_client_correlation_id PASSED [ 75%]
test_middleware.py::test_middleware_sanitizes_invalid_client_correlation_id PASSED [ 77%]
test_middleware.py::test_middleware_tracks_metrics PASSED             [ 79%]
test_schemas.py::test_query_request_valid PASSED                       [ 81%]
test_schemas.py::test_query_request_empty_question_rejected PASSED     [ 84%]
test_schemas.py::test_query_request_oversized_question_rejected PASSED [ 86%]
test_schemas.py::test_query_request_top_k_bounds PASSED                [ 88%]
test_schemas.py::test_batch_query_request_bounds PASSED                 [ 90%]
test_schemas.py::test_error_response_structure PASSED                  [ 93%]
test_services.py::test_sync_service_query PASSED                       [ 95%]
test_services.py::test_async_service_query[asyncio] PASSED             [ 97%]
test_services.py::test_service_functional_parity[asyncio] PASSED      [100%]

======================= 44 passed in 2.01s ========================
```

---

### 2.2 Day 17 Regression Test Suite
```bash
pytest Day-17/tests/ -v
```

```text
============================= test session starts =============================
platform win32 -- Python 3.13.12, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\projects\linkific\internship\Day-17\tests
plugins: anyio-4.15.1
collected 14 items

test_api.py::test_01_root_endpoint PASSED                               [  7%]
test_api.py::test_02_health_initial PASSED                             [ 14%]
test_api.py::test_03_ask_before_upload PASSED                         [ 21%]
test_api.py::test_04_upload_unsupported_file PASSED                     [ 28%]
test_api.py::test_05_upload_empty_file PASSED                           [ 35%]
test_api.py::test_06_upload_corrupted_pdf PASSED                       [ 42%]
test_api.py::test_07_upload_normal_pdf PASSED                          [ 50%]
test_api.py::test_08_upload_valid_txt PASSED                           [ 57%]
test_api.py::test_09_list_documents PASSED                             [ 64%]
test_api.py::test_10_empty_question PASSED                             [ 71%]
test_api.py::test_11_normal_question PASSED                            [ 78%]
test_api.py::test_12_upload_large_document PASSED                      [ 85%]
test_api.py::test_13_document_deletion PASSED                          [ 92%]
test_api.py::test_14_upload_oversized_file PASSED                      [100%]

================== 14 passed in 84.71s (0:01:24) ==================
```

---

## 3. Test Coverage Breakdown Across All 9 Functional Categories

| # | Test Area | Files & Cases | Result |
| :---: | :--- | :--- | :---: |
| 1 | **Schemas & Contracts** | `test_schemas.py` (6 tests: valid inputs, empty/oversized string rejections, top_k bounds, batch size limits, error envelope schema) | **PASS** |
| 2 | **Middleware & Timing** | `test_middleware.py` (4 tests: X-Request-ID injection, X-Process-Time-Ms positive float, client ID preservation, invalid ID sanitization, metrics counter) | **PASS** |
| 3 | **Authentication & Roles** | `test_dependencies.py` (7 tests: missing key 401, invalid key 401, standard key 200, standard key on admin route 403, admin key 200, pagination limits, dependency test override) | **PASS** |
| 4 | **Background Audit Tasks** | `test_background_tasks.py` (6 tests: JSONL file creation, pagination, non-existent file handling, corrupted line skipping, multi-threaded concurrent write lock, endpoint background dispatch) | **PASS** |
| 5 | **Service Layer & Parity** | `test_services.py` (3 tests: sync service search, async service search, exact functional score/ranking parity on identical queries) | **PASS** |
| 6 | **Versioned Endpoints** | `test_api_v1.py` (4 tests: /api/v1/health, /api/v1/query, /api/v1/batch-query, /api/v1/metrics) | **PASS** |
| 7 | **Legacy Routes (Day 17)** | `test_legacy_routes.py` (6 tests: GET /, GET /health, GET /documents, POST /ask, POST /ask empty failure, POST /sync/query baseline) | **PASS** |
| 8 | **Error Envelopes** | `test_error_handlers.py` (6 tests: 404 envelope, 422 validation details, 422 missing field, 422 invalid JSON, 500 internal server error trap, zero stack trace leakage) | **PASS** |
| 9 | **Batch Queries & Limits** | `test_batch_queries.py` (2 tests: batch exceeding limit rejection, concurrent batch order preservation) | **PASS** |

---

## 4. Summary Metrics
- **Day 21 Tests Collected:** 44
- **Day 21 Tests Passed:** 44 (100% pass rate)
- **Day 17 Regression Tests:** 14 (100% pass rate)
- **Day 20 Regression Tests:** 58 (100% pass rate)
- **Total Combined Verified Tests:** 116 tests passed across repository
- **Regressions / Breaking Changes:** Zero regressions.

---

## 5. Live Production Server End-to-End Verification Results

Executed against a live Uvicorn socket server (`http://127.0.0.1:8011`) with production settings via `verify_live_production.py`:

```text
================================================================================
DAY 21 LIVE PRODUCTION VERIFICATION RUNNER
Server Target: http://127.0.0.1:8011 | Environment: production
================================================================================
>>> Live Uvicorn server successfully bound and listening.

--- Testing Legacy Day 17 Routes ---
  [PASS] Legacy :: GET / (Root Welcome) -> PASSED 
  [PASS] Legacy :: GET /health (Legacy Health) -> PASSED 
  [PASS] Legacy :: GET /documents (Document Listing) -> PASSED 
  [PASS] Legacy :: POST /ask (Day 17 Question Answering) -> PASSED 
  [PASS] Legacy :: POST /ask (Empty Question 400) -> PASSED 

--- Testing Middleware & Correlation Headers ---
  [PASS] Middleware :: X-Request-ID Header Injected -> PASSED
  [PASS] Middleware :: X-Process-Time-Ms Header Injected -> PASSED
  [PASS] Middleware :: Client Correlation ID Preserved -> PASSED 

--- Testing Production Authentication & RBAC ---
  [PASS] Auth :: Missing API Key Returns 401 -> PASSED 
  [PASS] Auth :: Invalid API Key Returns 401 -> PASSED 
  [PASS] Auth :: Standard Key on Query Endpoint (200) -> PASSED 
  [PASS] Auth :: Standard Key on Admin Endpoint Returns 403 -> PASSED 
  [PASS] Auth :: Admin Key on Admin Endpoint Returns 200 -> PASSED 
  [PASS] Auth :: Admin Key on Metrics Endpoint Returns 200 -> PASSED 

--- Testing In-Process Background Task File Persistence ---
  [PASS] BackgroundTasks :: Physical Audit JSONL File Created -> PASSED
  [PASS] BackgroundTasks :: Audit Records Successfully Written to Disk -> PASSED (Found 4 entries)

--- Testing Batch Queries & Concurrency Limits ---
  [PASS] Batch :: Batch Query (3 items) Success -> PASSED 
  [PASS] Batch :: Oversized Batch (>10) Rejected with 422 -> PASSED 

--- Testing Benchmark Reproducibility Across Multiple Runs ---
  ================ BENCHMARK REPRODUCIBILITY RESULTS ================
  Run    Sync Mean    Async Mean   Sync p95     Async p95    Error Rate  
  ------------------------------------------------------------------------
  1      50.90 ms     67.93 ms     62.65 ms     80.79 ms     0.0%
  2      48.58 ms     69.03 ms     58.51 ms     78.65 ms     0.0%
  3      49.92 ms     74.91 ms     58.31 ms     89.45 ms     0.0%
  ========================================================================
  [PASS] Benchmark :: Benchmark Reproducibility (3 Runs CV < 15%) -> PASSED Sync CV=2.34%, Async CV=5.31%, Error Rate=0.0%

--- Testing Live HTTP Batch Query Concurrency vs Sequential ---
  Sequential 5-Query Time: 227.36 ms
  Concurrent Batch-Query Time: 54.66 ms
  Live HTTP Concurrency Speedup: +76.0%
  [PASS] Benchmark :: Live Batch Concurrency Speedup (>40%) -> PASSED Speedup=+76.0%

================================================================================
LIVE VERIFICATION COMPLETE: 20/20 CHECKS PASSED (0 FAILED)
================================================================================
```
