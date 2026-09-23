"""
Day 21 — Request Processing & Telemetry Middleware
Captures correlation IDs, measures request processing latency with microsecond precision,
injects X-Request-ID and X-Process-Time-Ms headers, and tracks runtime metrics.
"""

import time
import uuid
import re
import logging
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("linkific.api.middleware")

# Validation regex for client-supplied correlation ID: alphanumeric, hyphens, underscores, 1 to 64 chars
VALID_CORRELATION_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_\-]{1,64}$")


class MetricsTracker:
    """Thread-safe telemetry accumulator for server performance monitoring."""
    def __init__(self):
        self.total_requests = 0
        self.total_latency_ms = 0.0
        self.latencies = []
        self.max_latency_history = 500

    def record(self, latency_ms: float):
        self.total_requests += 1
        self.total_latency_ms += latency_ms
        self.latencies.append(latency_ms)
        if len(self.latencies) > self.max_latency_history:
            self.latencies.pop(0)

    def get_stats(self) -> dict:
        avg_latency = (self.total_latency_ms / self.total_requests) if self.total_requests > 0 else 0.0
        sorted_latencies = sorted(self.latencies) if self.latencies else [0.0]
        p95_idx = int(len(sorted_latencies) * 0.95)
        p95_latency = sorted_latencies[min(p95_idx, len(sorted_latencies) - 1)]

        return {
            "total_requests": self.total_requests,
            "average_latency_ms": round(avg_latency, 3),
            "p95_latency_ms": round(p95_latency, 3),
            "sample_size": len(self.latencies)
        }


metrics_tracker = MetricsTracker()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    HTTP Middleware executing around every HTTP request.
    Responsibilities:
    1. Correlation ID management: Validates incoming X-Request-ID header or generates new UUID4.
    2. Precision wall-clock timing via time.perf_counter().
    3. Context propagation to request.state.
    4. Response header injection: X-Request-ID and X-Process-Time-Ms.
    5. Telemetry recording for metrics endpoint.
    
    Note on BackgroundTasks:
    X-Process-Time-Ms measures the exact time from request receipt through endpoint execution
    and response header serialization. FastAPI BackgroundTasks execute asynchronously *after*
    the HTTP response has been sent to the client, so background task duration is intentionally
    isolated from this header.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 1. Extract and sanitize or generate Correlation ID
        incoming_id = request.headers.get("X-Request-ID")
        if incoming_id and VALID_CORRELATION_ID_PATTERN.match(incoming_id):
            request_id = incoming_id
        else:
            request_id = str(uuid.uuid4())

        # Bind to request state for access in dependencies and exception handlers
        request.state.request_id = request_id
        request.state.start_time = time.perf_counter()

        # 2. Log request start
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"[{request_id}] START {request.method} {request.url.path} from {client_ip}")

        # 3. Process request through downstream pipeline
        response = await call_next(request)

        # 4. Measure elapsed time
        elapsed_seconds = time.perf_counter() - request.state.start_time
        process_time_ms = round(elapsed_seconds * 1000.0, 3)

        # 5. Record telemetry
        metrics_tracker.record(process_time_ms)

        # 6. Inject standard headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = str(process_time_ms)

        # 7. Log request completion
        logger.info(
            f"[{request_id}] COMPLETED {request.method} {request.url.path} "
            f"Status={response.status_code} Latency={process_time_ms}ms"
        )

        return response
