"""
Day 21 — Live Production Environment Verification Script
Conducts live HTTP end-to-end testing against an active Uvicorn server:
1. Boots live server on dedicated port (8011) with production settings
2. Verifies all Legacy Day 17 routes (GET /, GET /health, GET /documents, POST /ask)
3. Verifies Middleware headers (X-Request-ID, X-Process-Time-Ms)
4. Verifies Production Authentication & RBAC (401 Missing/Invalid, 403 Standard on Admin, 200 Admin)
5. Verifies Background Task execution by checking physical JSONL audit file on disk
6. Verifies Bounded Batch Queries (semaphore concurrency & limit enforcement)
7. Executes 3 consecutive benchmark runs to prove reproducibility across runs
"""

import os
import sys
import time
import json
import uuid
import socket
import threading
import httpx
import uvicorn

# Ensure Day-21 root is on sys.path
DAY21_DIR = os.path.dirname(os.path.abspath(__file__))
if DAY21_DIR not in sys.path:
    sys.path.insert(0, DAY21_DIR)

TEST_PORT = 8011
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"

# Production Credentials for live verification
PROD_USER_KEY = "live-prod-user-key-2026"
PROD_ADMIN_KEY = "live-prod-admin-key-2026"

# Configure environment before importing app
os.environ["LINKIFIC_ENV"] = "production"
os.environ["LINKIFIC_API_KEY"] = PROD_USER_KEY
os.environ["LINKIFIC_ADMIN_API_KEY"] = PROD_ADMIN_KEY

LIVE_AUDIT_FILE = os.path.join(DAY21_DIR, "data", "test_live_audit.jsonl")
if os.path.exists(LIVE_AUDIT_FILE):
    os.remove(LIVE_AUDIT_FILE)
os.environ["AUDIT_LOG_FILE"] = LIVE_AUDIT_FILE

from app.config import settings
settings.LINKIFIC_ENV = "production"
settings.LINKIFIC_API_KEY = PROD_USER_KEY
settings.LINKIFIC_ADMIN_API_KEY = PROD_ADMIN_KEY
settings.AUDIT_LOG_FILE = LIVE_AUDIT_FILE

from app.main import create_app

app = create_app()


class UvicornServerThread(threading.Thread):
    def __init__(self, app, host="127.0.0.1", port=TEST_PORT):
        super().__init__(daemon=True)
        self.server = uvicorn.Server(
            config=uvicorn.Config(app=app, host=host, port=port, log_level="warning")
        )

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True


def wait_for_server(port, timeout=10.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.1)
    return False


def run_live_verification():
    print("=" * 80)
    print("DAY 21 LIVE PRODUCTION VERIFICATION RUNNER")
    print(f"Server Target: {BASE_URL}")
    print(f"Environment:   {settings.LINKIFIC_ENV}")
    print(f"Audit Log:     {LIVE_AUDIT_FILE}")
    print("=" * 80)

    # 1. Start Live Server in Background Thread
    server_thread = UvicornServerThread(app=app, port=TEST_PORT)
    server_thread.start()
    if not wait_for_server(TEST_PORT):
        print("ERROR: Failed to connect to live server within timeout!")
        sys.exit(1)
    print(">>> Live Uvicorn server successfully bound and listening.")

    results = []

    def record_check(category, name, passed, detail=""):
        status = "PASSED" if passed else "FAILED"
        results.append((category, name, status, detail))
        mark = "PASS" if passed else "FAIL"
        print(f"  [{mark}] {category} :: {name} -> {status} {detail}")

    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        # ----------------------------------------------------------------------
        # Section A: Legacy Day 17 Routes Verification
        # ----------------------------------------------------------------------
        print("\n--- Testing Legacy Day 17 Routes ---")
        
        # 1. GET /
        r = client.get("/")
        record_check("Legacy", "GET / (Root Welcome)", r.status_code == 200 and "Linkific Enterprise AI Service" in r.text)

        # 2. GET /health
        r = client.get("/health")
        data = r.json()
        record_check("Legacy", "GET /health (Legacy Health)", r.status_code == 200 and data.get("status") == "healthy" and data.get("total_indexed_documents", 0) > 0)

        # 3. GET /documents
        r = client.get("/documents")
        data = r.json()
        record_check("Legacy", "GET /documents (Document Listing)", r.status_code == 200 and data.get("total_documents", 0) >= 5)

        # 4. POST /ask (valid)
        r = client.post("/ask", json={"question": "What is the remote work policy?", "top_k": 2})
        data = r.json()
        record_check("Legacy", "POST /ask (Day 17 Question Answering)", r.status_code == 200 and len(data.get("sources", [])) > 0)

        # 5. POST /ask (empty question error handling)
        r = client.post("/ask", json={"question": ""})
        record_check("Legacy", "POST /ask (Empty Question 400)", r.status_code == 400)

        # ----------------------------------------------------------------------
        # Section B: Middleware Header Injection & Timing
        # ----------------------------------------------------------------------
        print("\n--- Testing Middleware & Correlation Headers ---")
        
        r = client.get("/api/v1/health")
        has_req_id = "x-request-id" in r.headers
        has_proc_time = "x-process-time-ms" in r.headers
        record_check("Middleware", "X-Request-ID Header Injected", has_req_id, f"ID={r.headers.get('x-request-id')}")
        record_check("Middleware", "X-Process-Time-Ms Header Injected", has_proc_time, f"Time={r.headers.get('x-process-time-ms')}")

        # Client-supplied correlation ID preservation
        client_id = f"corr-{uuid.uuid4().hex[:8]}"
        r = client.get("/api/v1/health", headers={"X-Request-ID": client_id})
        record_check("Middleware", "Client Correlation ID Preserved", r.headers.get("x-request-id") == client_id)

        # ----------------------------------------------------------------------
        # Section C: Production Authentication & Authorization
        # ----------------------------------------------------------------------
        print("\n--- Testing Production Authentication & RBAC ---")

        # 1. Missing API Key -> 401
        r = client.post("/api/v1/query", json={"question": "What are the core work hours?"})
        err_code = r.json().get("error", {}).get("code")
        record_check("Auth", "Missing API Key Returns 401", r.status_code == 401 and err_code == "UNAUTHORIZED")

        # 2. Invalid API Key -> 401
        r = client.post("/api/v1/query", json={"question": "What are the core work hours?"}, headers={"X-API-Key": "invalid-key"})
        err_code = r.json().get("error", {}).get("code")
        record_check("Auth", "Invalid API Key Returns 401", r.status_code == 401 and err_code == "UNAUTHORIZED")

        # 3. Standard User Key on User Endpoint -> 200
        r = client.post("/api/v1/query", json={"question": "What are the core work hours?"}, headers={"X-API-Key": PROD_USER_KEY})
        record_check("Auth", "Standard Key on Query Endpoint (200)", r.status_code == 200 and r.json().get("execution_mode") == "async")

        # 4. Standard User Key on Admin Endpoint -> 403 Forbidden
        r = client.get("/api/v1/audit/logs", headers={"X-API-Key": PROD_USER_KEY})
        err_code = r.json().get("error", {}).get("code")
        record_check("Auth", "Standard Key on Admin Endpoint Returns 403", r.status_code == 403 and err_code == "FORBIDDEN")

        # 5. Admin Key on Admin Endpoint -> 200 OK
        r = client.get("/api/v1/audit/logs", headers={"X-API-Key": PROD_ADMIN_KEY})
        record_check("Auth", "Admin Key on Admin Endpoint Returns 200", r.status_code == 200 and r.json().get("total_records", -1) >= 0)

        # 6. Admin Key on Metrics Endpoint -> 200 OK
        r = client.get("/api/v1/metrics", headers={"X-API-Key": PROD_ADMIN_KEY})
        metrics = r.json()
        record_check("Auth", "Admin Key on Metrics Endpoint Returns 200", r.status_code == 200 and metrics.get("total_requests_processed", 0) > 0)

        # ----------------------------------------------------------------------
        # Section D: Background Tasks & Physical File Persistence
        # ----------------------------------------------------------------------
        print("\n--- Testing In-Process Background Task File Persistence ---")
        
        # Fire 3 authenticated queries to generate audit records
        for i in range(3):
            client.post("/api/v1/query", json={"question": f"Live background test query #{i+1}"}, headers={"X-API-Key": PROD_USER_KEY})
        
        # Give FastAPI background worker a brief moment to flush
        time.sleep(0.5)

        file_exists = os.path.exists(LIVE_AUDIT_FILE)
        record_count = 0
        if file_exists:
            with open(LIVE_AUDIT_FILE, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
                record_count = len(lines)
        
        record_check("BackgroundTasks", "Physical Audit JSONL File Created", file_exists, f"Path={LIVE_AUDIT_FILE}")
        record_check("BackgroundTasks", "Audit Records Successfully Written to Disk", record_count >= 4, f"Found {record_count} entries")

        # ----------------------------------------------------------------------
        # Section E: Bounded Batch Queries
        # ----------------------------------------------------------------------
        print("\n--- Testing Batch Queries & Concurrency Limits ---")
        
        batch_payload = {
            "queries": [
                {"question": "What is the remote work policy?"},
                {"question": "What are the core hours?"},
                {"question": "What hardware allowance is provided?"}
            ]
        }
        r = client.post("/api/v1/batch-query", json=batch_payload, headers={"X-API-Key": PROD_USER_KEY})
        batch_data = r.json()
        record_check("Batch", "Batch Query (3 items) Success", r.status_code == 200 and batch_data.get("total_queries") == 3)

        # Oversized batch exceeding max limit (10 items max, send 12)
        oversized_payload = {"queries": [{"question": f"Question {i}"} for i in range(12)]}
        r = client.post("/api/v1/batch-query", json=oversized_payload, headers={"X-API-Key": PROD_USER_KEY})
        record_check("Batch", "Oversized Batch (>10) Rejected with 422", r.status_code == 422)

        # ----------------------------------------------------------------------
        # Section F: Benchmark Reproducibility Across Multiple Runs
        # ----------------------------------------------------------------------
        print("\n--- Testing Benchmark Reproducibility Across Multiple Runs ---")
        import asyncio
        import statistics
        from benchmark import run_full_benchmark

        runs = []
        for run_idx in range(1, 4):
            print(f"  >>> Executing Benchmark Round {run_idx} of 3 (N=30, C=5)...")
            bench_res = asyncio.run(run_full_benchmark(
                base_url=BASE_URL,
                num_requests=30,
                concurrency=5,
                warmup_count=3,
                api_key=PROD_USER_KEY
            ))
            
            s_sync = bench_res["concurrent_workload"]["synchronous_baseline"]
            s_async = bench_res["concurrent_workload"]["asynchronous_optimized"]
            comp = bench_res["concurrent_workload"]["comparison"]
            
            runs.append({
                "run": run_idx,
                "sync_mean": s_sync["mean_ms"],
                "async_mean": s_async["mean_ms"],
                "sync_p95": s_sync["p95_ms"],
                "async_p95": s_async["p95_ms"],
                "sync_rps": s_sync["throughput_rps"],
                "async_rps": s_async["throughput_rps"],
                "error_rate": s_sync["error_rate_pct"] + s_async["error_rate_pct"]
            })

        print("\n  ================ BENCHMARK REPRODUCIBILITY RESULTS ================")
        print(f"  {'Run':<6} {'Sync Mean':<12} {'Async Mean':<12} {'Sync p95':<12} {'Async p95':<12} {'Error Rate':<12}")
        print("  " + "-" * 72)
        for r_data in runs:
            print(f"  {r_data['run']:<6} {r_data['sync_mean']:<12.2f} {r_data['async_mean']:<12.2f} {r_data['sync_p95']:<12.2f} {r_data['async_p95']:<12.2f} {r_data['error_rate']:.1f}%")
        print("  " + "=" * 72)

        sync_means = [r["sync_mean"] for r in runs]
        async_means = [r["async_mean"] for r in runs]
        sync_cv = (statistics.stdev(sync_means) / statistics.mean(sync_means)) * 100.0
        async_cv = (statistics.stdev(async_means) / statistics.mean(async_means)) * 100.0

        is_reproducible = (sync_cv < 15.0) and (async_cv < 15.0) and all(r["error_rate"] == 0.0 for r in runs)
        record_check("Benchmark", "Benchmark Reproducibility (3 Runs CV < 15%)", is_reproducible, f"Sync CV={sync_cv:.2f}%, Async CV={async_cv:.2f}%, Error Rate=0.0%")

        # Live Batch Query Concurrency Speedup Test
        print("\n--- Testing Live HTTP Batch Query Concurrency vs Sequential ---")
        test_questions = [
            "What is the remote work policy?",
            "What are the core hours?",
            "What hardware allowance is provided?",
            "What is the code review standard?",
            "What are leave and attendance policies?"
        ]
        
        # Sequential calls to /sync/query
        t0 = time.perf_counter()
        for q in test_questions:
            client.post("/sync/query", json={"question": q, "top_k": 2}, headers={"X-API-Key": PROD_USER_KEY})
        seq_duration_ms = (time.perf_counter() - t0) * 1000.0

        # Single batch call to /api/v1/batch-query
        t0 = time.perf_counter()
        client.post("/api/v1/batch-query", json={"queries": [{"question": q, "top_k": 2} for q in test_questions]}, headers={"X-API-Key": PROD_USER_KEY})
        batch_duration_ms = (time.perf_counter() - t0) * 1000.0

        batch_speedup_pct = ((seq_duration_ms - batch_duration_ms) / seq_duration_ms) * 100.0
        print(f"  Sequential 5-Query Time: {seq_duration_ms:.2f} ms")
        print(f"  Concurrent Batch-Query Time: {batch_duration_ms:.2f} ms")
        print(f"  Live HTTP Concurrency Speedup: +{batch_speedup_pct:.1f}%")
        record_check("Benchmark", "Live Batch Concurrency Speedup (>40%)", batch_speedup_pct > 40.0, f"Speedup=+{batch_speedup_pct:.1f}%")

    # Clean shutdown
    server_thread.stop()
    print("\n>>> Live server shutdown completed.")

    # Summary
    total_checks = len(results)
    passed_checks = sum(1 for _, _, status, _ in results if status == "PASSED")
    failed_checks = total_checks - passed_checks

    print("\n" + "=" * 80)
    print(f"LIVE VERIFICATION COMPLETE: {passed_checks}/{total_checks} CHECKS PASSED ({failed_checks} FAILED)")
    print("=" * 80)

    # Clean up test audit log
    if os.path.exists(LIVE_AUDIT_FILE):
        os.remove(LIVE_AUDIT_FILE)

    if failed_checks > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_live_verification()
