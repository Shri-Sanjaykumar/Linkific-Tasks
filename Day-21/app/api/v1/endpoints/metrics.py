"""
Day 21 — v1 Metrics & Middleware Telemetry Endpoint
Exposes live middleware latency statistics, request counters, and p95 benchmarks.
"""

import time
import threading
from fastapi import APIRouter
from ....schemas import MetricsResponse
from ....middleware import metrics_tracker
from ....config import settings

router = APIRouter()


@router.get(
    "/metrics",
    response_model=MetricsResponse,
    tags=["Diagnostics & Health"]
)
async def v1_metrics():
    """
    Returns live server performance metrics collected by RequestLoggingMiddleware.
    Includes request counts, average latency, and p95 latency.
    """
    stats = metrics_tracker.get_stats()
    uptime = round(time.time() - getattr(settings, "_start_time", time.time()), 2)

    return MetricsResponse(
        total_requests_processed=stats["total_requests"],
        average_process_time_ms=stats["average_latency_ms"],
        p95_process_time_ms=stats["p95_latency_ms"],
        uptime_seconds=uptime,
        active_worker_threads=threading.active_count()
    )
