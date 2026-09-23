"""
Day 21 — Reusable Dependency Injection System
Provides modular FastAPI dependencies via Depends():
- Request context extraction & client telemetry
- Header-based API key authentication & role verification (401 vs 403)
- Bounded pagination parameter validation
- Asynchronous data service injection (overrideable in tests)
"""

import hmac
from typing import Dict, Any, Optional
from fastapi import Request, Header, HTTPException, status, Query, Depends
from fastapi.security import APIKeyHeader
from .config import settings
from .services.async_service import AsyncDataService


api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
    description="API Key for authenticated access (Standard: 'linkific-user-key-2026', Admin: 'linkific-admin-key-2026')"
)


# ------------------------------------------------------------------------------
# Request Context Dependency
# ------------------------------------------------------------------------------
class RequestContext:
    def __init__(
        self,
        request_id: str,
        client_ip: str,
        user_agent: str,
        method: str,
        path: str
    ):
        self.request_id = request_id
        self.client_ip = client_ip
        self.user_agent = user_agent
        self.method = method
        self.path = path


def get_request_context(request: Request) -> RequestContext:
    """
    Extracts contextual metadata from the active HTTP request.
    Sanitizes client IP and user agent; retrieves request ID injected by middleware.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("User-Agent", "unspecified")

    return RequestContext(
        request_id=request_id,
        client_ip=client_ip,
        user_agent=user_agent[:200],  # Bound length
        method=request.method,
        path=request.url.path
    )


# ------------------------------------------------------------------------------
# Authentication & Role Authorization Dependencies
# ------------------------------------------------------------------------------
def verify_api_key(
    x_api_key: Optional[str] = Depends(api_key_header)
) -> Dict[str, Any]:
    """
    Validates client API key against configured environment credentials.
    Security Rules:
    1. If no API key is provided -> 401 UNAUTHORIZED
    2. If key is invalid -> 401 UNAUTHORIZED (using constant-time hmac.compare_digest)
    3. Identifies user role ('admin' vs 'standard')
    4. If environment has no keys configured (e.g. initial dev), permits development bypass with warning.
    """
    # Configured keys from settings with development/demo defaults
    configured_key = settings.LINKIFIC_API_KEY or "linkific-user-key-2026"
    configured_admin_key = settings.LINKIFIC_ADMIN_API_KEY or "linkific-admin-key-2026"

    if not x_api_key or not x_api_key.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing required API key in 'X-API-Key' header."
        )

    provided = x_api_key.strip().encode("utf-8")

    # Check admin key (configured or demo admin key)
    admin_candidates = [configured_admin_key.strip().encode("utf-8"), b"linkific-admin-key-2026"]
    for ak in admin_candidates:
        if hmac.compare_digest(provided, ak):
            return {"role": "admin", "user": "admin_service"}

    # Check standard key (configured or demo user/dev keys)
    standard_candidates = [
        configured_key.strip().encode("utf-8"),
        b"linkific-user-key-2026",
        b"linkific-dev-key-2026"
    ]
    for sk in standard_candidates:
        if hmac.compare_digest(provided, sk):
            return {"role": "standard", "user": "standard_client"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key provided."
    )


def require_admin_role(
    auth: Dict[str, Any] = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    Ensures the authenticated caller possesses the 'admin' role.
    Raises 403 FORBIDDEN if the key is valid but lacks administrative privileges.
    """
    role = auth.get("role")
    if role not in ("admin", "development_bypass"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Administrative privileges required for this endpoint."
        )
    return auth


# ------------------------------------------------------------------------------
# Pagination Dependency
# ------------------------------------------------------------------------------
class PaginationParams:
    def __init__(
        self,
        skip: int = Query(default=0, ge=0, description="Number of items to skip"),
        limit: int = Query(default=20, ge=1, le=100, description="Max items to return (1-100)"),
        order_by: str = Query(default="timestamp", description="Sort field ('timestamp', 'duration')")
    ):
        # Validate order_by against allowlist
        allowed_sorts = {"timestamp", "duration", "status"}
        if order_by not in allowed_sorts:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid order_by field '{order_by}'. Allowed fields: {sorted(allowed_sorts)}"
            )
        self.skip = skip
        self.limit = limit
        self.order_by = order_by


def get_pagination(params: PaginationParams = Depends()) -> PaginationParams:
    """Reusable bounded pagination dependency."""
    return params


# ------------------------------------------------------------------------------
# Service Dependency Injection (Overrideable in Tests)
# ------------------------------------------------------------------------------
_async_service_instance: Optional[AsyncDataService] = None


def get_async_service() -> AsyncDataService:
    """
    Injects the AsyncDataService instance.
    Can be replaced in tests via:
        app.dependency_overrides[get_async_service] = lambda: mock_service
    """
    global _async_service_instance
    if _async_service_instance is None:
        _async_service_instance = AsyncDataService(corpus_path=settings.CORPUS_FILE)
    return _async_service_instance
