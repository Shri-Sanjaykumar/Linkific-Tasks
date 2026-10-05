"""
Linkific Enterprise AI Service - Main FastAPI Application
Production-ready REST microservice featuring structured logging, Prometheus metrics,
correlation ID tracing, and multi-agent workflow automation endpoints.
"""

from contextlib import asynccontextmanager
from collections import defaultdict
import threading
import time
import uuid
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI, Request, Response, Header, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse

from app.core.config import get_settings, Settings
from app.core.logging_config import setup_logging, get_logger, set_correlation_id, get_correlation_id
from app.core.metrics import metrics_registry
from app.schemas import (
    WorkflowRequest,
    WorkflowResponse,
    FinanceApprovalRequest,
    FinanceApprovalResponse,
    ApprovalTier,
    HealthResponse,
    ComponentStatus,
    SystemInfoResponse
)
from app.graph import execute_multi_agent_workflow

# Initialize logger
logger = get_logger("LinkificService.API")


# ==============================================================================
# Application Lifespan Events
# ==============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes logging and pre-warms resources on startup; cleans up on shutdown."""
    settings = get_settings()
    setup_logging(
        level=settings.LOG_LEVEL,
        log_format=settings.LOG_FORMAT,
        log_file_path=settings.LOG_FILE_PATH,
        service_name=settings.APP_NAME,
        environment=settings.ENVIRONMENT,
        max_bytes=settings.LOG_ROTATION_BYTES,
        backup_count=settings.LOG_BACKUP_COUNT
    )
    logger.info(
        f"Service '{settings.APP_NAME}' v{settings.APP_VERSION} starting up | "
        f"Environment: {settings.ENVIRONMENT} | Host: {settings.HOST}:{settings.PORT}"
    )
    yield
    logger.info(f"Service '{settings.APP_NAME}' shutting down gracefully.")



class SlidingWindowRateLimiter:
    """
    Thread-safe in-memory sliding window rate limiter.
    Enforces RATE_LIMIT_PER_MINUTE threshold per client IP across API endpoints.
    """
    def __init__(self, limit: int = 120):
        self.limit = limit
        self.lock = threading.Lock()
        self.records = defaultdict(list)

    def is_allowed(self, client_id: str) -> tuple[bool, int]:
        now = time.time()
        window = 60.0
        with self.lock:
            # Clean timestamps older than sliding 60-second window
            self.records[client_id] = [t for t in self.records[client_id] if now - t < window]
            if len(self.records[client_id]) >= self.limit:
                oldest = self.records[client_id][0]
                retry_after = max(1, int(window - (now - oldest)))
                return False, retry_after
            self.records[client_id].append(now)
            return True, 0

    def reset(self):
        with self.lock:
            self.records.clear()


# ==============================================================================
# FastAPI App Factory
# ==============================================================================
def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Production Automation and Multi-Agent Intelligence Platform for Linkific.",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )

    # 1. CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    rate_limiter = SlidingWindowRateLimiter(limit=settings.RATE_LIMIT_PER_MINUTE)
    app.state.rate_limiter = rate_limiter

    # 2. Correlation ID, Observability & Rate-Limiting Middleware
    @app.middleware("http")
    async def observability_middleware(request: Request, call_next):
        # Extract or generate correlation ID
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = f"CORR-{uuid.uuid4().hex[:12].upper()}"
        set_correlation_id(correlation_id)

        # Enforce rate limiting on API endpoints (exempting health/readiness/metrics probes)
        path = request.url.path
        if not path.startswith("/health") and path != "/metrics":
            client_ip = request.client.host if request.client else "127.0.0.1"
            allowed, retry_after = rate_limiter.is_allowed(client_ip)
            if not allowed:
                logger.warning(
                    f"Rate limit exceeded for client {client_ip} on {path} (Limit: {settings.RATE_LIMIT_PER_MINUTE}/min)"
                )
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Too Many Requests",
                        "detail": f"Rate limit of {settings.RATE_LIMIT_PER_MINUTE} requests per minute exceeded.",
                        "correlation_id": correlation_id
                    },
                    headers={
                        "Retry-After": str(retry_after),
                        "X-Correlation-ID": correlation_id
                    }
                )

        start_time = time.time()
        path = request.url.path
        method = request.method

        try:
            response: Response = await call_next(request)
            duration = round(time.time() - start_time, 4)

            # Record metrics and access logs
            metrics_registry.record_http_request(
                method=method,
                endpoint=path,
                status_code=response.status_code,
                duration_seconds=duration
            )

            # Attach tracing header to response
            response.headers["X-Correlation-ID"] = get_correlation_id()
            response.headers["X-Response-Time-Ms"] = str(round(duration * 1000, 2))

            logger.info(
                f"{method} {path} -> {response.status_code} in {round(duration * 1000, 2)}ms"
            )
            return response

        except Exception as exc:
            duration = round(time.time() - start_time, 4)
            metrics_registry.record_http_request(
                method=method,
                endpoint=path,
                status_code=500,
                duration_seconds=duration
            )
            logger.exception(f"Unhandled exception processing {method} {path}: {str(exc)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal Server Error",
                    "details": str(exc),
                    "correlation_id": correlation_id
                },
                headers={"X-Correlation-ID": correlation_id}
            )

    # ==========================================================================
    # Security Dependencies
    # ==========================================================================
    def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> str:
        """Verifies API Key for protected endpoints."""
        current_settings = get_settings()
        if not x_api_key or x_api_key != current_settings.API_KEY:
            logger.warning(f"Unauthorized access attempt with invalid or missing API key.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing X-API-Key authentication header."
            )
        return x_api_key

    # ==========================================================================
    # Core Health & Monitoring Endpoints
    # ==========================================================================
    @app.get("/", tags=["General"])
    async def root():
        """Root endpoint returning service identity and navigation links."""
        current_settings = get_settings()
        return {
            "service": current_settings.APP_NAME,
            "version": current_settings.APP_VERSION,
            "environment": current_settings.ENVIRONMENT,
            "status": "OPERATIONAL",
            "documentation": "/docs",
            "probes": {
                "liveness": "/health/live",
                "readiness": "/health/ready",
                "metrics": "/metrics"
            }
        }

    @app.get("/health/live", tags=["Observability"])
    async def liveness_probe():
        """Kubernetes/Docker liveness probe: indicates process is responsive."""
        return {
            "status": "alive",
            "uptime_seconds": metrics_registry.get_uptime_seconds()
        }

    @app.get("/health/ready", response_model=HealthResponse, tags=["Observability"])
    async def readiness_probe():
        """
        Kubernetes/Docker readiness probe: verifies all sub-components
        (corpus data, logging, configuration) before accepting live traffic.
        """
        current_settings = get_settings()
        components = {}
        all_healthy = True

        # 1. Document Corpus Check
        corpus_path = Path(current_settings.DOCS_CORPUS_PATH)
        if not corpus_path.exists():
            corpus_path = Path(__file__).resolve().parent.parent / "data" / "company_docs.json"

        if corpus_path.exists():
            try:
                with open(corpus_path, "r", encoding="utf-8") as f:
                    docs = json.load(f)
                components["document_corpus"] = ComponentStatus(
                    name="Enterprise Policy Corpus",
                    status="healthy",
                    details=f"Loaded {len(docs)} documents successfully."
                )
            except Exception as e:
                all_healthy = False
                components["document_corpus"] = ComponentStatus(
                    name="Enterprise Policy Corpus",
                    status="unhealthy",
                    details=f"Failed to read corpus: {str(e)}"
                )
        else:
            all_healthy = False
            components["document_corpus"] = ComponentStatus(
                name="Enterprise Policy Corpus",
                status="unhealthy",
                details=f"Corpus file missing at '{corpus_path}'."
            )

        # 2. Logging Subsystem Check
        log_dir = Path(current_settings.LOG_FILE_PATH).parent
        if log_dir.exists() and os.access(log_dir, os.W_OK):
            components["logging_subsystem"] = ComponentStatus(
                name="Structured Audit Logging",
                status="healthy",
                details=f"Writable log destination at '{current_settings.LOG_FILE_PATH}'."
            )
        else:
            components["logging_subsystem"] = ComponentStatus(
                name="Structured Audit Logging",
                status="degraded",
                details=f"Log directory '{log_dir}' not writable; falling back to stdout."
            )

        # 3. Multi-Agent Engine Check
        from app.graph import LANGGRAPH_AVAILABLE
        components["workflow_engine"] = ComponentStatus(
            name="LangGraph Multi-Agent Engine",
            status="healthy",
            details="Official LangGraph CompiledStateGraph loaded." if LANGGRAPH_AVAILABLE else "Fallback runtime active."
        )

        overall_status = "healthy" if all_healthy else "unhealthy"
        status_code = status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

        resp = HealthResponse(
            status=overall_status,
            app_name=current_settings.APP_NAME,
            version=current_settings.APP_VERSION,
            environment=current_settings.ENVIRONMENT,
            uptime_seconds=metrics_registry.get_uptime_seconds(),
            components=components
        )
        return JSONResponse(status_code=status_code, content=resp.model_dump())

    @app.get("/metrics", response_class=PlainTextResponse, tags=["Observability"])
    async def prometheus_metrics():
        """Prometheus metric exposition endpoint formatted per OpenMetrics standards."""
        return PlainTextResponse(
            content=metrics_registry.format_prometheus_metrics(),
            media_type="text/plain; version=0.0.4; charset=utf-8"
        )

    # ==========================================================================
    # Enterprise Service & API Endpoints
    # ==========================================================================
    @app.get("/api/v1/system/info", response_model=SystemInfoResponse, tags=["System"])
    async def get_system_info(api_key: str = Depends(verify_api_key)):
        """Returns safe system configuration and metadata for authorized operators."""
        current_settings = get_settings()
        corpus_path = Path(current_settings.DOCS_CORPUS_PATH)
        if not corpus_path.exists():
            corpus_path = Path(__file__).resolve().parent.parent / "data" / "company_docs.json"

        doc_count = 0
        if corpus_path.exists():
            try:
                with open(corpus_path, "r", encoding="utf-8") as f:
                    doc_count = len(json.load(f))
            except Exception:
                pass

        return SystemInfoResponse(
            app_name=current_settings.APP_NAME,
            version=current_settings.APP_VERSION,
            environment=current_settings.ENVIRONMENT,
            debug=current_settings.DEBUG,
            logging_level=current_settings.LOG_LEVEL,
            metrics_enabled=current_settings.METRICS_ENABLED,
            corpus_document_count=doc_count
        )

    @app.post("/api/v1/workflow/run", response_model=WorkflowResponse, tags=["Multi-Agent Workflow"])
    async def run_workflow(
        request: WorkflowRequest,
        http_response: Response,
        api_key: str = Depends(verify_api_key)
    ):
        """
        Executes the LangGraph Multi-Agent Research & Intelligence Workflow.
        Supports 'streamlined' (4 hops) and 'comprehensive' (6 hops) execution topologies.
        """
        cid = request.correlation_id or get_correlation_id()
        http_response.headers["X-Correlation-ID"] = cid
        logger.info(f"API received workflow request [mode={request.mode}]: '{request.query}'")

        response = execute_multi_agent_workflow(
            query=request.query,
            mode=request.mode,
            correlation_id=cid
        )
        return response

    @app.post("/api/v1/finance/invoice-approval", response_model=FinanceApprovalResponse, tags=["Finance Automation"])
    async def process_finance_invoice(
        req: FinanceApprovalRequest,
        api_key: str = Depends(verify_api_key)
    ):
        """
        Linkific Core Finance Automation: Evaluates vendor invoices against purchase orders
        and routes approval based on automated threshold gates.
        """
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        audit_id = f"AUD-FIN-{uuid.uuid4().hex[:8].upper()}"

        # Rule 1: Validate PO format
        has_valid_po = bool(req.po_number and req.po_number.startswith("PO-"))

        # Rule 2: Tier Evaluation
        if not has_valid_po:
            status_val = "flagged"
            tier = ApprovalTier.REJECTED
            signers = ["Procurement Compliance"]
            auto_approved = False
            reason = "Invalid purchase order reference. Invoice must reference a valid PO-XXXX number."
        elif req.amount <= 1000.0:
            status_val = "approved"
            tier = ApprovalTier.STRAIGHT_THROUGH
            signers = ["Automated Straight-Through Processing (STP)"]
            auto_approved = True
            reason = "Amount under $1,000 threshold with valid PO match. Straight-Through Processing applied."
        elif req.amount <= 10000.0:
            status_val = "pending_approval"
            tier = ApprovalTier.MANAGER_APPROVAL
            signers = ["Finance Department Manager"]
            auto_approved = False
            reason = "Amount between $1,000 and $10,000 threshold requires Department Manager sign-off."
        else:
            status_val = "pending_approval"
            tier = ApprovalTier.DIRECTOR_APPROVAL
            signers = ["Finance Director", "VP of Finance"]
            auto_approved = False
            reason = "Amount exceeds $10,000 threshold requiring dual executive sign-off and compliance review."

        metrics_registry.record_finance_approval(status=status_val, tier=tier.value)
        logger.info(f"Finance invoice '{req.invoice_id}' (${req.amount}) processed: {status_val} ({tier.value})")

        return FinanceApprovalResponse(
            invoice_id=req.invoice_id,
            po_number=req.po_number,
            vendor_name=req.vendor_name,
            amount=req.amount,
            currency=req.currency,
            status=status_val,
            approval_tier=tier,
            required_signers=signers,
            matched_po=has_valid_po,
            auto_approved=auto_approved,
            audit_id=audit_id,
            timestamp=now_iso,
            routing_reason=reason
        )

    return app


# Application instance for ASGI runners (uvicorn app.main:app)
app = create_app()
