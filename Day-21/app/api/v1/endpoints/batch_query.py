"""
Day 21 — v1 Concurrent Batch Query Endpoint
Executes multiple independent queries concurrently using asyncio.gather().
Features bounded semaphore concurrency, per-item timeouts, preserved result ordering,
and granular per-query error reporting.
"""

import time
from fastapi import APIRouter, Depends, HTTPException, status
from ....schemas import (
    BatchQueryRequest,
    BatchQueryResponse,
    BatchQueryItemResult,
    QueryResponse,
    DocumentRecord
)
from ....dependencies import verify_api_key, get_request_context, RequestContext, get_async_service
from ....services.async_service import AsyncDataService
from ....config import settings

router = APIRouter()


@router.post(
    "/batch-query",
    response_model=BatchQueryResponse,
    status_code=status.HTTP_200_OK,
    tags=["Query & Document Operations"],
    responses={
        400: {"description": "Exceeded maximum batch limit"},
        401: {"description": "Missing or invalid API key"},
        422: {"description": "Pydantic validation failure"}
    }
)
async def v1_batch_query(
    request_body: BatchQueryRequest,
    auth: dict = Depends(verify_api_key),
    context: RequestContext = Depends(get_request_context),
    service: AsyncDataService = Depends(get_async_service)
):
    """
    Executes multiple queries concurrently:
    1. Validates batch size <= settings.MAX_BATCH_SIZE (default 10).
    2. Runs queries concurrently using asyncio.gather() bounded by Semaphore(5).
    3. Traps timeouts and failures individually per item, preserving input order.
    4. Returns comprehensive summary with counts and itemized status.
    """
    if len(request_body.queries) > settings.MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Batch size of {len(request_body.queries)} exceeds maximum allowed limit of {settings.MAX_BATCH_SIZE}."
        )

    start_t = time.perf_counter()
    questions = [q.question for q in request_body.queries]

    # Execute concurrent bounded batch
    raw_batch_results = await service.batch_query_async(
        questions=questions,
        top_k=3,
        simulate_io_delay=0.04,
        max_concurrency=5,
        timeout_seconds=settings.QUERY_TIMEOUT_SECONDS
    )

    formatted_items = []
    success_count = 0
    fail_count = 0

    for item in raw_batch_results:
        idx = item["index"]
        status_str = item["status"]
        err = item.get("error")

        if status_str == "success":
            success_count += 1
            query_res = QueryResponse(
                question=item["question"],
                matched_count=len(item["results"]),
                results=[DocumentRecord(**r) for r in item["results"]],
                execution_mode="async_batch",
                duration_ms=round((time.perf_counter() - start_t) * 1000.0, 3),
                request_id=f"{context.request_id}-item-{idx}"
            )
            formatted_items.append(BatchQueryItemResult(
                index=idx,
                status="success",
                result=query_res,
                error=None
            ))
        else:
            fail_count += 1
            formatted_items.append(BatchQueryItemResult(
                index=idx,
                status=status_str,
                result=None,
                error=err or "Unknown processing failure"
            ))

    total_elapsed_ms = round((time.perf_counter() - start_t) * 1000.0, 3)

    return BatchQueryResponse(
        total_queries=len(request_body.queries),
        successful_queries=success_count,
        failed_queries=fail_count,
        results=formatted_items,
        total_duration_ms=total_elapsed_ms,
        request_id=context.request_id
    )
