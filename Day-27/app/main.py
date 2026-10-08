"""FastAPI Application Entrypoint for FinDoc-AuditEngine."""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.routers import audit
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise Financial Document Reconciliation, ML Anomaly Scoring & Dual Currency Audit Microservice.",
)

# Include API router
app.include_router(audit.router, prefix=f"{settings.API_V1_STR}/audit", tags=["Financial Audit"])


@app.get("/", include_in_schema=False)
def root():
    """Redirect root access directly to interactive Swagger docs."""
    return RedirectResponse(url="/docs")


@app.get("/health/live", tags=["Health"])
def liveness_probe():
    return {"status": "LIVE", "service": settings.APP_NAME}


@app.get("/health/ready", tags=["Health"])
def readiness_probe():
    return {
        "status": "READY",
        "service": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION,
        "dual_currency_usd_inr": settings.USD_TO_INR_RATE,
        "dependencies": {
            "ml_anomaly_scorer": "INITIALIZED",
            "reconciliation_engine": "ACTIVE",
        },
    }
