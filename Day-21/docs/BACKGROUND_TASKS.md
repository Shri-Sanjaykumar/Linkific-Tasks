# Day 21 — In-Process Background Tasks & Audit Logging

## 1. Concept and Mechanism

FastAPI provides an in-process `BackgroundTasks` mechanism that allows endpoints to schedule non-critical operations to run immediately after the HTTP response has been delivered to the client.

In Day 21, the application uses `BackgroundTasks` to record audit and activity events to a persistent JSON Lines file (`data/activity_audit.jsonl`).

```python
@router.post("/query")
async def v1_query(
    request_body: QueryRequest,
    background_tasks: BackgroundTasks,
    context: RequestContext = Depends(get_request_context),
    service: AsyncDataService = Depends(get_async_service)
):
    results = await service.query_async(request_body.question)

    # Schedule background audit write without delaying HTTP response delivery
    background_tasks.add_task(
        write_audit_log_entry,
        request_id=context.request_id,
        event="query_completed",
        endpoint=context.path,
        status="success",
        duration_ms=elapsed_ms,
        client_ip=context.client_ip
    )

    return QueryResponse(...)
```

---

## 2. In-Process Concurrency & Thread-Safety

Because FastAPI worker threads can handle concurrent requests simultaneously, uncontrolled concurrent file writes to the same file descriptor can cause race conditions and interleaved JSON records.

To guarantee atomic write operations, `app/background_tasks.py` uses a standard Python `threading.Lock()`:

```python
_file_write_lock = threading.Lock()

def write_audit_log_entry(...):
    with _file_write_lock:
        with open(target_file, "a", encoding="utf-8") as f:
            f.write(json_line)
```

### Structured JSON Lines Record Format:
```json
{
  "timestamp": "2026-09-23T11:31:26.123456Z",
  "request_id": "955673a6-519f-4c95-bd80-73ee5eeed03f",
  "event": "query_completed",
  "endpoint": "/api/v1/query",
  "status": "success",
  "duration_ms": 166.77,
  "client_ip": "127.0.0.1",
  "metadata": {
    "question": "What are the core hours and remote hardware allowance?",
    "matched_count": 3,
    "auth_role": "standard"
  }
}
```

---

## 3. Critical Limitations: In-Process vs Distributed Task Queues

> [!WARNING]
> **FastAPI BackgroundTasks vs Distributed Brokers:**
> FastAPI `BackgroundTasks` execute **in-process** within the memory space of the active web worker process. They are suitable for light, non-critical background actions (such as access logging, cache eviction, or activity records). They are **NOT** a replacement for distributed message queues.

| Feature | FastAPI BackgroundTasks (In-Process) | Distributed Task Queue (Celery / Redis / Kafka) |
| :--- | :--- | :--- |
| **Execution Environment** | Same Python process / worker memory | Dedicated external worker pool / machines |
| **Crash Durability** | **None.** If the process restarts or crashes, pending tasks are lost permanently. | **High.** Tasks are persisted in durable brokers (Redis, RabbitMQ, SQS, Kafka) and retried. |
| **Retry Policies** | None (unless manually coded in function) | Configurable exponential backoff, dead-letter queues, jitter |
| **Heavy Computation** | Competes with HTTP server for CPU and memory | Isolated on dedicated background worker clusters |
| **Horizontal Scaling** | Bound to individual server instance | Workers can scale independently from API web servers |
| **Complexity & Overhead** | Zero extra dependencies or infrastructure | Requires message broker daemon, worker daemon, and monitoring |
