"""
Day 21 — Master v1 API Router
Aggregates all versioned endpoints under prefix '/api/v1'.
"""

from fastapi import APIRouter
from .endpoints.health import router as health_router
from .endpoints.query import router as query_router
from .endpoints.batch_query import router as batch_router
from .endpoints.audit import router as audit_router
from .endpoints.metrics import router as metrics_router

v1_router = APIRouter(prefix="/api/v1")

# Include sub-routers
v1_router.include_router(health_router)
v1_router.include_router(query_router)
v1_router.include_router(batch_router)
v1_router.include_router(audit_router)
v1_router.include_router(metrics_router)
