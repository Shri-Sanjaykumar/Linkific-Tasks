# Day 21 — Asynchronous Programming & Concurrency in FastAPI

## 1. Architectural Overview & Event Loop Mechanics

Asynchronous programming in Python leverages the `asyncio` event loop to execute non-blocking cooperative multitasking on a single thread. In standard synchronous programming, any I/O operation (reading files from disk, waiting for database query responses, or issuing outbound HTTP requests) blocks the operating system thread until the hardware or network finishes. Under concurrent user traffic, this creates severe request queueing, threadpool starvation, and latency degradation.

In FastAPI, endpoints declared with `async def` run directly on the application's central event loop. 

```
                +------------------------------------+
                |       FastAPI Event Loop           |
                +-----------------+------------------+
                                  |
            +---------------------+---------------------+
            |                                           |
            v                                           v
    [Async Coroutine]                           [Async Coroutine]
  (await asyncio.sleep)                        (await aiofiles.read)
            |                                           |
     Yields Control                              Yields Control
  to Event Loop for I/O                       to Event Loop for I/O
            |                                           |
            +---------------------+---------------------+
                                  |
                                  v
                +------------------------------------+
                |  Event Loop Processes Other Tasks  |
                +-----------------+------------------+
                                  |
                 I/O Complete -> Resumes Execution
```

> [!CAUTION]
> **The Classic Async Anti-Pattern:** Merely adding the `async def` label to an endpoint that performs blocking synchronous calls (such as `time.sleep()`, standard `open()`, or heavy CPU computation) freezes the entire event loop, stopping *all other* concurrent requests from being processed until the blocking call finishes.

---

## 2. I/O-Bound vs CPU-Bound Execution Strategies

In Day 21, the application explicitly differentiates between I/O-bound tasks and CPU-bound tasks:

| Workload Category | Operation Example in Day 21 | Selected Execution Strategy | Why This Strategy Was Chosen |
| :--- | :--- | :--- | :--- |
| **I/O-Bound: File Access** | Reading document corpus (`data/sample_docs.json`) | `aiofiles.open()` (with fallback to `anyio.to_thread.run_sync`) | Asynchronous non-blocking file streaming yields control back to the event loop while disk heads/caches respond. |
| **I/O-Bound: External Network / DB** | Simulating remote database query or vector search latency | `await asyncio.sleep(0.04)` | Cooperative sleep pauses only the calling coroutine without consuming CPU cycles or blocking thread resources. |
| **CPU-Bound: Tokenization & Scoring** | Regex token normalization, term-frequency calculation, relevance ranking | `await anyio.to_thread.run_sync(_score_documents)` | Python's Global Interpreter Lock (GIL) limits CPU-intensive Python computation to one core per thread. Offloading to AnyIO's worker threadpool keeps the async event loop responsive. |
| **I/O-Bound: Multiple Queries** | Processing batch queries concurrently | `await asyncio.gather(*tasks)` bounded by `asyncio.Semaphore(5)` | Concurrently dispatches independent queries, interleaving their I/O wait states while capping concurrency to prevent resource exhaustion. |

---

## 3. Implementation Code Breakdown

### 3.1 Non-Blocking File I/O (`app/services/async_service.py`)
```python
async def load_documents_async(self) -> List[Dict[str, Any]]:
    if not os.path.exists(self.corpus_path):
        return []

    if HAS_AIOFILES:
        async with aiofiles.open(self.corpus_path, mode="r", encoding="utf-8") as f:
            content = await f.read()
        return json.loads(content)
    else:
        def _sync_read():
            with open(self.corpus_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return await anyio.to_thread.run_sync(_sync_read)
```

### 3.2 Threadpool Offloading for CPU-Bound Text Scoring
```python
def _score_documents():
    query_terms = set(self._normalize_tokens_cpu(question))
    if not query_terms:
        return []
    scored = []
    for doc in docs:
        doc_terms = set(self._normalize_tokens_cpu(doc.get("title", "") + " " + doc.get("content", "")))
        overlap = query_terms.intersection(doc_terms)
        score = round(len(overlap) / max(len(query_terms), 1), 4)
        if score > 0:
            d = dict(doc)
            d["score"] = score
            scored.append(d)
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]

# Run CPU work in worker threadpool, freeing the event loop
scored_docs = await anyio.to_thread.run_sync(_score_documents)
```

### 3.3 Bounded Concurrency with Semaphores & Timeouts
```python
semaphore = asyncio.Semaphore(max_concurrency)

async def _run_single(idx: int, q: str) -> Dict[str, Any]:
    async with semaphore:
        try:
            res = await asyncio.wait_for(
                self.query_async(q, top_k=top_k, simulate_io_delay=simulate_io_delay),
                timeout=timeout_seconds
            )
            return {"index": idx, "status": "success", "results": res, "error": None}
        except asyncio.TimeoutError:
            return {"index": idx, "status": "timeout", "results": [], "error": "Query timed out."}
```

---

## 4. Key Takeaways & Best Practices
1. **Never Block the Event Loop:** Always use `await` on genuine async calls or offload blocking/CPU calls to threadpools using `anyio.to_thread.run_sync` or `fastapi.concurrency.run_in_threadpool`.
2. **Bound Concurrency:** Do not use unbounded `asyncio.gather(*[...])` with thousands of items; use `asyncio.Semaphore` to cap simultaneous tasks.
3. **Always Enforce Timeouts:** Protect asynchronous pipelines with `asyncio.wait_for(coro, timeout=...)` to prevent hung sockets from leaking memory and tasks indefinitely.
