"""
Day 21 — Linkific Enterprise AI Service Main Application
Integrates Async Programming, Request Logging Middleware, In-Process Background Tasks,
Dependency Injection, API Versioning (/api/v1), and Framework-Level Exception Handlers.
"""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import settings
from .middleware import RequestLoggingMiddleware
from .exceptions import (
    http_exception_handler,
    starlette_http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from .background_tasks import ensure_audit_dir
from .api.legacy import legacy_router
from .api.v1.router import v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan managing startup bootstrap and shutdown events."""
    # Record startup timestamp for uptime tracking
    settings._start_time = time.time()

    # Ensure data directory and audit log directories are prepared safely
    ensure_audit_dir()

    yield

    # Clean shutdown tasks if any
    pass


def create_app() -> FastAPI:
    """Factory function creating the configured FastAPI application instance."""
    app = FastAPI(
        title=settings.APP_NAME,
        description="""
**Linkific AI/ML Internship — Day 21: Enterprise FastAPI Architecture**

Demonstrates:
- **Async Programming & Async/Await:** Non-blocking file I/O, threadpool offloading, and concurrent batch retrieval.
- **Custom Middleware:** High-precision execution timing (`X-Process-Time-Ms`) and correlation tracking (`X-Request-ID`).
- **In-Process Background Tasks:** Non-critical JSON Lines audit logging decoupled from client response latency.
- **Modular Dependency Injection:** Request context extraction, API key authentication, role checks, and pagination.
- **API Versioning:** Clean `/api/v1` routes preserving legacy unversioned endpoints.
- **Scientific Benchmarking:** Validated synchronous baseline vs asynchronous concurrency measurements.
        """,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    # 1. Register Middleware Stack
    app.add_middleware(RequestLoggingMiddleware)

    # 2. Register Centralized Exception Handlers
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # 3. Include Routers (Legacy first for backward compatibility, then /api/v1)
    app.include_router(legacy_router)
    app.include_router(v1_router)

    return app


app = create_app()
