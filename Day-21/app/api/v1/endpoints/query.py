"""
Day 21 — v1 Asynchronous Query Endpoint
Executes non-blocking document search, leverages dependency injection for auth,
request context, and service, and enqueues in-process background audit tasks.
"""

import time
from fastapi import APIRouter, Depends, BackgroundTasks, status
from ....schemas import QueryRequest, QueryResponse, DocumentRecord
from ....dependencies import verify_api_key, get_request_context, RequestContext, get_async_service
from ....services.async_service import AsyncDataService
from ....background_tasks import write_audit_log_entry

router = APIRouter()


@router.post(
    "/query",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    tags=["Query & Document Operations"],
    responses={
        401: {"description": "Missing or invalid API key"},
        422: {"description": "Pydantic validation failure"}
    }
)
async def v1_query(
    request_body: QueryRequest,
    background_tasks: BackgroundTasks,
    auth: dict = Depends(verify_api_key),
    context: RequestContext = Depends(get_request_context),
    service: AsyncDataService = Depends(get_async_service)
):
    """
    Executes non-blocking asynchronous document search:
    1. Validates API key via dependency injection.
    2. Retrieves context metadata (request ID, client IP).
    3. Runs non-blocking asynchronous document query.
    4. Schedules non-critical audit log write via FastAPI BackgroundTasks.
    5. Returns response immediately without waiting for audit file I/O.
    """
    start_t = time.perf_counter()

    # Execute non-blocking query
    raw_results = await service.query_async(
        question=request_body.question,
        top_k=request_body.top_k,
        category=request_body.category,
        simulate_io_delay=0.04
    )

    elapsed_ms = round((time.perf_counter() - start_t) * 1000.0, 3)

    # Schedule non-blocking in-process audit logging
    background_tasks.add_task(
        write_audit_log_entry,
        request_id=context.request_id,
        event="query_completed",
        endpoint=context.path,
        status="success",
        duration_ms=elapsed_ms,
        client_ip=context.client_ip,
        metadata={
            "question": request_body.question[:100],
            "matched_count": len(raw_results),
            "auth_role": auth.get("role", "anonymous")
        }
    )

    return QueryResponse(
        question=request_body.question,
        matched_count=len(raw_results),
        results=[DocumentRecord(**r) for r in raw_results],
        execution_mode="async",
        duration_ms=elapsed_ms,
        request_id=context.request_id
    )
