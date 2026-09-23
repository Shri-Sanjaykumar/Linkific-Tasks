"""
Day 21 — v1 Health Diagnostics Endpoint
Provides system telemetry, uptime, operational mode, and corpus statistics.
"""

import time
from fastapi import APIRouter, Depends
from ....schemas import HealthResponse
from ....config import settings
from ....services.async_service import AsyncDataService
from ....dependencies import get_async_service

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Diagnostics & Health"])
async def v1_health(service: AsyncDataService = Depends(get_async_service)):
    """
    Health check for version 1 API.
    Returns operational status, uptime, worker mode, and count of indexed documents.
    """
    docs = await service.load_documents_async()
    uptime = round(time.time() - getattr(settings, "_start_time", time.time()), 2)

    return HealthResponse(
        status="healthy",
        uptime_seconds=uptime,
        version=settings.APP_VERSION,
        environment=settings.LINKIFIC_ENV,
        worker_mode="asynchronous_event_loop",
        total_indexed_documents=len(docs)
    )
