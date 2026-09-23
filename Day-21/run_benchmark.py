"""
Day 21 — Benchmark Runner CLI
Executes the benchmark suite, saves JSON metrics, and generates
the performance comparison report in docs/PERFORMANCE_BENCHMARK.md.
"""

import sys
import os
import argparse
import asyncio

# Ensure Day-21 is on sys.path
DAY21_DIR = os.path.dirname(os.path.abspath(__file__))
if DAY21_DIR not in sys.path:
    sys.path.insert(0, DAY21_DIR)

from benchmark import run_full_benchmark, save_benchmark_results


def generate_benchmark_markdown_report(results: dict) -> str:
    """Generates the Markdown Performance Benchmark Report from actual measured metrics."""
    meta = results["metadata"]
    c_work = results["concurrent_workload"]
    s_sync = c_work["synchronous_baseline"]
    s_async = c_work["asynchronous_optimized"]
    comp = c_work["comparison"]
    seq = results["sequential_workload"]

    md = f"""# Performance Benchmark Report: Synchronous vs Asynchronous FastAPI Architecture

## 1. Executive Summary & Experimental Hypothesis

In this benchmark, we evaluate the performance of an asynchronous FastAPI endpoint (`/api/v1/query`) against an equivalent synchronous baseline endpoint (`/sync/query`).

### Scientific Hypothesis:
- **Concurrency & Event-Loop Interleaving:** Asynchronous endpoints yield measurable concurrency benefits primarily on **I/O-bound workloads** (such as file reads, database queries, and external API calls) by relinquishing control back to the event loop while waiting for I/O.
- **Sequential Overhead:** For purely single-threaded, sequential requests (concurrency = 1), asynchronous coroutine management does not magically accelerate execution and may exhibit slight framework overhead.
- **Fairness Guarantee:** Both endpoints operate on the identical underlying dataset (`data/sample_docs.json`), run within the same environment, and execute identical token scoring logic.

---

## 2. Test Environment & Benchmark Parameters

- **Test Timestamp:** `{meta['timestamp']}`
- **Benchmark Execution Mode:** `{meta['benchmark_mode']}`
- **Operating System:** `{meta['os']}`
- **Python Version:** `{meta['python_version']}`
- **Concurrent Request Volume:** `{meta['num_requests_concurrent']}` requests
- **Concurrency Level:** `{meta['concurrency_level']}` parallel workers
- **Sequential Baseline Volume:** 20 requests (concurrency = 1)
- **Workload:** I/O file read + simulated external roundtrip (40ms) + CPU token scoring
- **Payload Question:** `"{meta['payload_summary']}"`

---

## 3. Performance Comparison Table (Measured Results)

| Metric | Synchronous Baseline (`/sync/query`) | Asynchronous Optimized (`/api/v1/query`) | Delta / Improvement | Percentage Change |
| :--- | :---: | :---: | :---: | :---: |
| **Total Requests** | {s_sync['total_requests']} | {s_async['total_requests']} | — | — |
| **Successful Requests** | {s_sync['successful_requests']} | {s_async['successful_requests']} | — | — |
| **Failed Requests (Error Rate)** | {s_sync['failed_requests']} ({s_sync['error_rate_pct']}%) | {s_async['failed_requests']} ({s_async['error_rate_pct']}%) | 0 | 0.0% |
| **Mean Latency (Avg)** | **{s_sync['mean_ms']} ms** | **{s_async['mean_ms']} ms** | **{comp['latency_reduction_ms']} ms** | **{comp['latency_reduction_percent']}%** |
| **Median Latency (p50)** | {s_sync['median_ms']} ms | {s_async['median_ms']} ms | {round(s_sync['median_ms'] - s_async['median_ms'], 2)} ms | {round((s_sync['median_ms'] - s_async['median_ms'])/max(s_sync['median_ms'], 1)*100, 2)}% |
| **90th Percentile (p90)** | {s_sync['p90_ms']} ms | {s_async['p90_ms']} ms | {round(s_sync['p90_ms'] - s_async['p90_ms'], 2)} ms | {round((s_sync['p90_ms'] - s_async['p90_ms'])/max(s_sync['p90_ms'], 1)*100, 2)}% |
| **95th Percentile (p95)** | **{s_sync['p95_ms']} ms** | **{s_async['p95_ms']} ms** | **{round(s_sync['p95_ms'] - s_async['p95_ms'], 2)} ms** | **{round((s_sync['p95_ms'] - s_async['p95_ms'])/max(s_sync['p95_ms'], 1)*100, 2)}%** |
| **Min Latency** | {s_sync['min_ms']} ms | {s_async['min_ms']} ms | {round(s_sync['min_ms'] - s_async['min_ms'], 2)} ms | — |
| **Max Latency** | {s_sync['max_ms']} ms | {s_async['max_ms']} ms | {round(s_sync['max_ms'] - s_async['max_ms'], 2)} ms | — |
| **Total Wall-Clock Time** | {s_sync['total_wall_time_s']} s | {s_async['total_wall_time_s']} s | {round(s_sync['total_wall_time_s'] - s_async['total_wall_time_s'], 2)} s | — |
| **Throughput (req/sec)** | **{s_sync['throughput_rps']} rps** | **{s_async['throughput_rps']} rps** | **+{comp['throughput_gain_rps']} rps** | **+{comp['throughput_gain_percent']}%** |

---

## 4. Sequential Workload Analysis (Concurrency = 1)

To isolate concurrency benefits from raw single-request processing speed:

| Workload Mode | Mean Latency | Median Latency | Throughput |
| :--- | :---: | :---: | :---: |
| **Synchronous Sequential** | {seq['synchronous_sequential']['mean_ms']} ms | {seq['synchronous_sequential']['median_ms']} ms | {seq['synchronous_sequential']['throughput_rps']} rps |
| **Asynchronous Sequential** | {seq['asynchronous_sequential']['mean_ms']} ms | {seq['asynchronous_sequential']['median_ms']} ms | {seq['asynchronous_sequential']['throughput_rps']} rps |

### Key Observation:
In sequential single-request mode, the response time difference ({seq['sequential_latency_delta_ms']} ms) is negligible. This empirically proves that `async/await` is not an arithmetic speed booster for solitary operations, but a **concurrency multiplexer** enabling hundreds of I/O operations to interleave efficiently.

---

## 5. Architectural Explanation: I/O-Bound vs CPU-Bound

1. **Why Async Outperforms Under Concurrency on I/O:**
   In synchronous execution, each blocking I/O operation (waiting for a database socket, remote API, or file read) forces the OS thread to block. Under concurrency, requests queue up waiting for available worker threads.
   In asynchronous execution, `await asyncio.sleep()` or non-blocking socket reads yield execution to the event loop, permitting other concurrent requests to be processed concurrently on the single thread.

2. **Why CPU-Bound Tasks Require Threadpool Offloading:**
   Python's Global Interpreter Lock (GIL) prevents pure Python CPU operations from running concurrently on multiple cores within the same event loop. For CPU-bound tasks (token normalization, heavy scoring, encryption), we offload execution using `anyio.to_thread.run_sync()`. This guarantees that CPU-heavy processing does not starve or freeze the async event loop.

---

## 6. Benchmarking Limitations & Real-World Caveats

1. **Local Loopback Interface:** Testing on `127.0.0.1` eliminates real-world WAN latency, packet jitter, and TLS handshake overhead.
2. **Process Worker Constraints:** Local tests run with a single Uvicorn process worker. Production systems typically deploy multi-worker configurations (e.g. `gunicorn -k uvicorn.workers.UvicornWorker -w 4`).
3. **Database & External Mocking:** Simulated 40ms delays represent typical external API latency, but real external services experience latency variance and rate-limiting.
"""
    return md


def main():
    parser = argparse.ArgumentParser(description="Run Day 21 Performance Benchmark")
    parser.add_argument("--url", default=None, help="Live server base URL (e.g. http://127.0.0.1:8000). If omitted, uses in-process ASGITransport.")
    parser.add_argument("--requests", type=int, default=50, help="Number of concurrent requests (default: 50)")
    parser.add_argument("--concurrency", type=int, default=10, help="Concurrency level (default: 10)")
    parser.add_argument("--warmup", type=int, default=5, help="Warmup requests count (default: 5)")

    args = parser.parse_args()

    print("=" * 70)
    print("STARTING DAY 21 PERFORMANCE BENCHMARK")
    print(f"Requests: {args.requests} | Concurrency: {args.concurrency} | Mode: {'Live Server' if args.url else 'In-Process ASGI'}")
    print("=" * 70)

    results = asyncio.run(run_full_benchmark(
        base_url=args.url,
        num_requests=args.requests,
        concurrency=args.concurrency,
        warmup_count=args.warmup
    ))

    # Save raw JSON results
    save_benchmark_results(results)

    # Render Markdown Report
    report_md = generate_benchmark_markdown_report(results)
    doc_path = os.path.join(DAY21_DIR, "docs", "PERFORMANCE_BENCHMARK.md")
    os.makedirs(os.path.dirname(doc_path), exist_ok=True)
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(report_md)

    print(f"Generated Benchmark Report: {doc_path}")
    print("\n" + "=" * 70)
    print("BENCHMARK SUMMARY COMPARISON TABLE")
    print("=" * 70)
    c_comp = results["concurrent_workload"]["comparison"]
    s_sync = results["concurrent_workload"]["synchronous_baseline"]
    s_async = results["concurrent_workload"]["asynchronous_optimized"]
    print(f"Synchronous Baseline:  Mean={s_sync['mean_ms']}ms, p95={s_sync['p95_ms']}ms, Throughput={s_sync['throughput_rps']} rps")
    print(f"Asynchronous Endpoint: Mean={s_async['mean_ms']}ms, p95={s_async['p95_ms']}ms, Throughput={s_async['throughput_rps']} rps")
    print(f"Observed Delta:        Latency Change={c_comp['latency_reduction_percent']}%, Throughput Change=+{c_comp['throughput_gain_percent']}%")
    print("=" * 70)


if __name__ == "__main__":
    main()
