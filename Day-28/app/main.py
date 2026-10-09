"""FinDoc-AuditEngine Enterprise Application Entrypoint.

Mounts static assets, serves the executive financial portal UI, registers
REST API endpoints, and configures enterprise global exception handlers.
"""

from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.core.logging_config import logger
from app.exceptions import FinDocAuditException
from app.routers import audit

# Application Directory Paths
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Initialize Enterprise FastAPI App
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Enterprise Financial Document Processing & Multi-Tier Audit Gateway with "
        "PII Scrubber, 3-Way Reconciliation, Isolation Forest ML Risk Scoring, and "
        "Dual Currency USD/INR Pegging at ₹86.50."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS Policy configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Assets & Template Engine
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# -------------------------------------------------------------------------
# Global Exception Handlers
# -------------------------------------------------------------------------

@app.exception_handler(FinDocAuditException)
async def handle_findoc_audit_exception(request: Request, exc: FinDocAuditException):
    """Structured handler for all domain audit exceptions."""
    logger.error(f"FinDoc Audit Domain Error [{exc.error_code}]: {exc.message} | Details: {exc.details}")
    return JSONResponse(
        status_code=exc.http_status,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": request.url.path,
        },
    )


# -------------------------------------------------------------------------
# Core Web & System Routes
# -------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse, tags=["Web Portal"])
@app.get("/dashboard", response_class=HTMLResponse, tags=["Web Portal"])
async def serve_dashboard(request: Request):
    """Serves the FinTech Executive Audit Portal Single Page Application."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "usd_to_inr_rate": settings.USD_TO_INR_RATE,
        },
    )


@app.get("/health", tags=["System Telemetry"])
async def system_health_check():
    """Enterprise Health Check Telemetry Endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pegged_usd_to_inr": settings.USD_TO_INR_RATE,
        "models": {
            "anomaly_detector": "IsolationForest_v2.0",
            "pii_scrubber": "Regex_PAN_Aadhaar_v2.0",
            "matching_engine": "ThreeWayReconciliation_v2.0",
        },
    }


# Include API Routers with standard versioned prefix
app.include_router(audit.router, prefix="/api/v1/audit", tags=["Audit Engine"])
