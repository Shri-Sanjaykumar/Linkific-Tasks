"""
Day 21 — v1 Audit Log Inspection Endpoint
Allows authorized administrative callers to inspect recorded in-process background audit logs.
Enforces strict role checks (require_admin_role) and bounded pagination.
"""

from fastapi import APIRouter, Depends, status
from ....schemas import AuditLogListResponse, AuditRecord
from ....dependencies import require_admin_role, get_pagination, PaginationParams
from ....background_tasks import read_audit_logs

router = APIRouter()


@router.get(
    "/audit/logs",
    response_model=AuditLogListResponse,
    status_code=status.HTTP_200_OK,
    tags=["Audit & Governance"],
    responses={
        401: {"description": "Missing or invalid API key"},
        403: {"description": "Forbidden: Requires admin role"},
        422: {"description": "Invalid pagination parameters"}
    }
)
async def v1_audit_logs(
    pagination: PaginationParams = Depends(get_pagination),
    auth: dict = Depends(require_admin_role)
):
    """
    Retrieves audit records created by BackgroundTasks:
    1. Enforces admin-level authentication.
    2. Enforces bounded pagination (skip >= 0, limit <= 100).
    3. Returns paginated JSON records with total count metadata.
    """
    total_count, records = read_audit_logs(skip=pagination.skip, limit=pagination.limit)

    return AuditLogListResponse(
        total_records=total_count,
        returned_records=len(records),
        skip=pagination.skip,
        limit=pagination.limit,
        records=[AuditRecord(**r) for r in records]
    )
