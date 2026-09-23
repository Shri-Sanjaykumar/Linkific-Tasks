"""
Day 21 — Global Exception Handlers
Provides centralized, safe, framework-level exception handling.
Ensures uniform error envelopes without leaking sensitive tracebacks or file paths to clients.
"""

import logging
import traceback
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("linkific.api.exceptions")


def _get_request_id(request: Request) -> str:
    """Safely extracts request ID from request state or headers."""
    if hasattr(request.state, "request_id"):
        return request.state.request_id
    return request.headers.get("X-Request-ID", "unknown")


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handles anticipated HTTP exceptions (e.g. 401 Unauthorized, 403 Forbidden, 404 Not Found).
    """
    request_id = _get_request_id(request)
    status_code = exc.status_code

    # Map status code to standard error code
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        408: "REQUEST_TIMEOUT",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_SERVER_ERROR",
        503: "SERVICE_UNAVAILABLE"
    }
    error_code = code_map.get(status_code, "HTTP_ERROR")

    # If detail is already a dict with code/message, preserve it
    if isinstance(exc.detail, dict):
        message = exc.detail.get("message", str(exc.detail))
        error_code = exc.detail.get("code", error_code)
    else:
        message = str(exc.detail)

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": error_code,
                "message": message,
                "request_id": request_id
            }
        }
    )


async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handles Starlette HTTP exceptions (like 404 from non-existent routes)."""
    return await http_exception_handler(request, HTTPException(status_code=exc.status_code, detail=exc.detail))


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handles Pydantic validation errors (HTTP 422).
    Formats granular error details cleanly without exposing internal code structures.
    """
    request_id = _get_request_id(request)
    details = []
    for err in exc.errors():
        field_path = " -> ".join(str(loc) for loc in err.get("loc", []) if loc != "body")
        details.append({
            "field": field_path or "root",
            "message": err.get("msg", "Invalid value"),
            "type": err.get("type", "value_error")
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request body or query parameter validation failed.",
                "request_id": request_id,
                "details": details
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Catches all unexpected internal exceptions (HTTP 500).
    Logs the full traceback to server stderr/logger, but returns a clean, safe
    error envelope to the HTTP client to prevent secret or path leakage.
    """
    request_id = _get_request_id(request)

    # Server-side logging of raw exception and traceback with correlation ID
    logger.error(
        f"[Request {request_id}] Unhandled Exception: {type(exc).__name__}: {str(exc)}\n"
        f"{traceback.format_exc()}"
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal server error occurred. Please contact support with the request ID.",
                "request_id": request_id
            }
        }
    )
