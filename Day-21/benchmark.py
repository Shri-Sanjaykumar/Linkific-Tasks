"""
Day 21 — Scientific Performance Benchmarking Suite
Executes controlled, reproducible performance benchmarks comparing synchronous baseline
and asynchronous endpoints under identical workloads, payloads, and concurrency levels.

Collects:
- Total requests, successful requests, failed requests, error rate
- Latency percentiles: min, mean, median (p50), p90, p95, max
- Throughput (requests / second)
- Relative performance changes calculated strictly from measured outputs without fabrication.
"""

import sys
import os
import time
import json
import statistics
import asyncio
from typing import Dict, Any, List, Optional
import httpx

# Ensure Day-21 is on sys.path
DAY21_DIR = os.path.dirname(os.path.abspath(__file__))
if DAY21_DIR not in sys.path:
    sys.path.insert(0, DAY21_DIR)

from app.main import app
from app.config import settings


class BenchmarkMetrics:
    """Computes statistical metrics over a sequence of latency samples."""
    def __init__(self, latencies_ms: List[float], failed_count: int, total_wall_time_s: float):
        self.total_requests = len(latencies_ms) + failed_count
        self.successful_requests = len(latencies_ms)
        self.failed_requests = failed_count
        self.error_rate_pct = round((failed_count / self.total_requests * 100.0) if self.total_requests > 0 else 0.0, 2)
        self.total_wall_time_s = round(total_wall_time_s, 4)
        self.throughput_rps = round((self.successful_requests / total_wall_time_s) if total_wall_time_s > 0 else 0.0, 2)

        if latencies_ms:
            sorted_lat = sorted(latencies_ms)
            self.min_ms = round(sorted_lat[0], 2)
            self.max_ms = round(sorted_lat[-1], 2)
            self.mean_ms = round(statistics.mean(latencies_ms), 2)
            self.median_ms = round(statistics.median(latencies_ms), 2)

            p90_idx = int(len(sorted_lat) * 0.90)
            self.p90_ms = round(sorted_lat[min(p90_idx, len(sorted_lat) - 1)], 2)

            p95_idx = int(len(sorted_lat) * 0.95)
            self.p95_ms = round(sorted_lat[min(p95_idx, len(sorted_lat) - 1)], 2)
        else:
            self.min_ms = 0.0
            self.max_ms = 0.0
            self.mean_ms = 0.0
            self.median_ms = 0.0
            self.p90_ms = 0.0
            self.p95_ms = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "error_rate_pct": self.error_rate_pct,
            "total_wall_time_s": self.total_wall_time_s,
            "throughput_rps": self.throughput_rps,
            "min_ms": self.min_ms,
            "mean_ms": self.mean_ms,
            "median_ms": self.median_ms,
            "p90_ms": self.p90_ms,
            "p95_ms": self.p95_ms,
            "max_ms": self.max_ms
        }


async def execute_request_pool(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    payload: Optional[dict],
    headers: Optional[dict],
    num_requests: int,
    concurrency: int
) -> BenchmarkMetrics:
    """
    Executes num_requests across concurrency simultaneous workers using an asyncio worker pool.
    Measures client-observed roundtrip latency per request.
    """
    semaphore = asyncio.Semaphore(concurrency)
    latencies: List[float] = []
    failures: int = 0

    async def _worker():
        nonlocal failures
        async with semaphore:
            t0 = time.perf_counter()
            try:
                if method.upper() == "POST":
                    resp = await client.post(url, json=payload, headers=headers)
                else:
                    resp = await client.get(url, headers=headers)

                dur_ms = (time.perf_counter() - t0) * 1000.0
                if resp.status_code in (200, 201):
                    latencies.append(dur_ms)
                else:
                    failures += 1
            except Exception:
                failures += 1

    wall_start = time.perf_counter()
    tasks = [asyncio.create_task(_worker()) for _ in range(num_requests)]
    await asyncio.gather(*tasks)
    total_wall_time = time.perf_counter() - wall_start

    return BenchmarkMetrics(latencies, failures, total_wall_time)


async def run_full_benchmark(
    base_url: Optional[str] = None,
    num_requests: int = 50,
    concurrency: int = 10,
    warmup_count: int = 5,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes the scientific benchmark comparing:
    1. Synchronous baseline endpoint (/sync/query)
    2. Asynchronous optimized endpoint (/api/v1/query)
    3. Sequential single-request comparison (concurrency = 1)
    """
    # Test payload identical for all runs
    test_payload = {
        "question": "What are the core hours and remote hardware allowance?",
        "top_k": 3
    }
    active_key = api_key or settings.LINKIFIC_API_KEY or "test-key-bench"
    test_headers = {
        "X-API-Key": active_key
    }

    # Set up client: use live URL if server is running, else use ASGITransport
    if base_url:
        client = httpx.AsyncClient(base_url=base_url, timeout=30.0)
        mode = "live_http_server"
    else:
        transport = httpx.ASGITransport(app=app)
        client = httpx.AsyncClient(transport=transport, base_url="http://testserver", timeout=30.0)
        mode = "in_process_asgi"

    async with client:
        # Override dependency or auth if needed
        # 1. Warm-up Phase
        print(f"Executing {warmup_count} warm-up requests to prime caches and JIT...")
        for _ in range(warmup_count):
            try:
                await client.post("/sync/query", json=test_payload, headers=test_headers)
                await client.post("/api/v1/query", json=test_payload, headers=test_headers)
            except Exception:
                pass

        # ----------------------------------------------------------------------
        # Benchmark 1: Concurrent I/O Workload (50 reqs, Concurrency = 10)
        # ----------------------------------------------------------------------
        print(f"\n[1/3] Benchmarking Concurrent Synchronous Baseline (/sync/query)...")
        sync_concurrent = await execute_request_pool(
            client=client,
            method="POST",
            url="/sync/query",
            payload=test_payload,
            headers=test_headers,
            num_requests=num_requests,
            concurrency=concurrency
        )
        print(f"    Completed: Mean={sync_concurrent.mean_ms}ms, p95={sync_concurrent.p95_ms}ms, Throughput={sync_concurrent.throughput_rps} rps")

        print(f"\n[2/3] Benchmarking Concurrent Asynchronous Endpoint (/api/v1/query)...")
        async_concurrent = await execute_request_pool(
            client=client,
            method="POST",
            url="/api/v1/query",
            payload=test_payload,
            headers=test_headers,
            num_requests=num_requests,
            concurrency=concurrency
        )
        print(f"    Completed: Mean={async_concurrent.mean_ms}ms, p95={async_concurrent.p95_ms}ms, Throughput={async_concurrent.throughput_rps} rps")

        # ----------------------------------------------------------------------
        # Benchmark 2: Sequential Workload (20 reqs, Concurrency = 1)
        # ----------------------------------------------------------------------
        print(f"\n[3/3] Benchmarking Sequential Single-Worker Workload (Concurrency = 1)...")
        sync_seq = await execute_request_pool(
            client=client,
            method="POST",
            url="/sync/query",
            payload=test_payload,
            headers=test_headers,
            num_requests=20,
            concurrency=1
        )

        async_seq = await execute_request_pool(
            client=client,
            method="POST",
            url="/api/v1/query",
            payload=test_payload,
            headers=test_headers,
            num_requests=20,
            concurrency=1
        )

    # Calculate real, un-fabricated comparisons
    latency_delta = round(sync_concurrent.mean_ms - async_concurrent.mean_ms, 2)
    pct_latency_change = round(((sync_concurrent.mean_ms - async_concurrent.mean_ms) / sync_concurrent.mean_ms * 100.0) if sync_concurrent.mean_ms > 0 else 0.0, 2)
    throughput_delta = round(async_concurrent.throughput_rps - sync_concurrent.throughput_rps, 2)
    pct_throughput_change = round(((async_concurrent.throughput_rps - sync_concurrent.throughput_rps) / sync_concurrent.throughput_rps * 100.0) if sync_concurrent.throughput_rps > 0 else 0.0, 2)

    results = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "benchmark_mode": mode,
            "python_version": sys.version.split()[0],
            "os": sys.platform,
            "num_requests_concurrent": num_requests,
            "concurrency_level": concurrency,
            "payload_summary": test_payload["question"]
        },
        "concurrent_workload": {
            "synchronous_baseline": sync_concurrent.to_dict(),
            "asynchronous_optimized": async_concurrent.to_dict(),
            "comparison": {
                "latency_reduction_ms": latency_delta,
                "latency_reduction_percent": pct_latency_change,
                "throughput_gain_rps": throughput_delta,
                "throughput_gain_percent": pct_throughput_change
            }
        },
        "sequential_workload": {
            "synchronous_sequential": sync_seq.to_dict(),
            "asynchronous_sequential": async_seq.to_dict(),
            "sequential_latency_delta_ms": round(sync_seq.mean_ms - async_seq.mean_ms, 2)
        }
    }

    return results


def save_benchmark_results(results: Dict[str, Any], output_dir: Optional[str] = None):
    """Saves baseline, async, and comparison JSON files."""
    out_dir = output_dir or os.path.join(DAY21_DIR, "outputs")
    os.makedirs(out_dir, exist_ok=True)

    # 1. Baseline
    with open(os.path.join(out_dir, "benchmark_baseline.json"), "w", encoding="utf-8") as f:
        json.dump(results["concurrent_workload"]["synchronous_baseline"], f, indent=2)

    # 2. Async
    with open(os.path.join(out_dir, "benchmark_async.json"), "w", encoding="utf-8") as f:
        json.dump(results["concurrent_workload"]["asynchronous_optimized"], f, indent=2)

    # 3. Full Comparison
    with open(os.path.join(out_dir, "benchmark_comparison.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nRaw benchmark metrics saved to: {out_dir}/")
