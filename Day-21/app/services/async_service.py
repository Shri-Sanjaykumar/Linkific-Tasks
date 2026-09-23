"""
Day 21 — Asynchronous Data Service (Optimized)
Implements non-blocking file I/O (aiofiles), non-blocking external I/O (asyncio.sleep),
threadpool offloading for CPU token normalization (anyio.to_thread.run_sync),
and bounded concurrent batch execution (asyncio.gather with Semaphore).
Maintains 100% functional parity with SyncDataService.
"""

import os
import json
import asyncio
import re
from typing import List, Dict, Any, Optional

try:
    import aiofiles
    HAS_AIOFILES = True
except ImportError:
    HAS_AIOFILES = False

import anyio


class AsyncDataService:
    """
    Non-blocking asynchronous document search and analytics service.
    Designed for high-throughput concurrency without blocking the FastAPI event loop.
    """

    def __init__(self, corpus_path: str):
        self.corpus_path = corpus_path

    async def load_documents_async(self) -> List[Dict[str, Any]]:
        """
        Asynchronously reads and parses the JSON corpus file.
        Uses aiofiles if available; otherwise offloads blocking read to threadpool.
        """
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

    @staticmethod
    def _normalize_tokens_cpu(text: str) -> List[str]:
        """CPU-intensive token extraction and normalization executed in worker thread."""
        tokens = re.findall(r"\b[a-zA-Z0-9_-]+\b", text.lower())
        term_freq = {}
        for t in tokens:
            term_freq[t] = term_freq.get(t, 0) + 1
        return [t for t in tokens if len(t) > 2]

    async def query_async(
        self,
        question: str,
        top_k: int = 3,
        category: Optional[str] = None,
        simulate_io_delay: float = 0.04
    ) -> List[Dict[str, Any]]:
        """
        Executes asynchronous non-blocking document retrieval:
        1. Non-blocking asynchronous file read.
        2. Non-blocking external I/O delay (await asyncio.sleep).
        3. CPU-intensive token scoring offloaded to threadpool.
        4. Category filtering and top-k ranking.
        """
        # 1. Non-blocking file I/O
        docs = await self.load_documents_async()

        # 2. Non-blocking external I/O (yields control to event loop)
        if simulate_io_delay > 0:
            await asyncio.sleep(simulate_io_delay)

        # 3. Offload CPU-bound token computation to worker thread
        def _score_documents():
            query_terms = set(self._normalize_tokens_cpu(question))
            if not query_terms:
                return []

            scored = []
            for doc in docs:
                if category and category.strip() and category.lower() != "string" and doc.get("category", "").lower() != category.lower():
                    continue

                doc_terms = set(self._normalize_tokens_cpu(doc.get("title", "") + " " + doc.get("content", "")))
                overlap = query_terms.intersection(doc_terms)
                score = round(len(overlap) / max(len(query_terms), 1), 4)

                if score > 0:
                    d = dict(doc)
                    d["score"] = score
                    scored.append(d)

            scored.sort(key=lambda x: x["score"], reverse=True)
            return scored[:top_k]

        scored_docs = await anyio.to_thread.run_sync(_score_documents)
        return scored_docs

    async def batch_query_async(
        self,
        questions: List[str],
        top_k: int = 3,
        simulate_io_delay: float = 0.04,
        max_concurrency: int = 5,
        timeout_seconds: float = 5.0
    ) -> List[Dict[str, Any]]:
        """
        Processes a batch of queries concurrently using asyncio.gather().
        Concurrency bounded by asyncio.Semaphore to prevent resource exhaustion.
        Per-item timeout prevents slow external tasks from hanging the entire batch.
        Preserves original question order in returned results.
        """
        semaphore = asyncio.Semaphore(max_concurrency)

        async def _run_single(idx: int, q: str) -> Dict[str, Any]:
            async with semaphore:
                try:
                    res = await asyncio.wait_for(
                        self.query_async(q, top_k=top_k, simulate_io_delay=simulate_io_delay),
                        timeout=timeout_seconds
                    )
                    return {
                        "index": idx,
                        "status": "success",
                        "question": q,
                        "results": res,
                        "error": None
                    }
                except asyncio.TimeoutError:
                    return {
                        "index": idx,
                        "status": "timeout",
                        "question": q,
                        "results": [],
                        "error": f"Query timed out after {timeout_seconds} seconds."
                    }
                except Exception as e:
                    return {
                        "index": idx,
                        "status": "error",
                        "question": q,
                        "results": [],
                        "error": f"{type(e).__name__}: {str(e)}"
                    }

        tasks = [_run_single(i, q) for i, q in enumerate(questions)]
        results = await asyncio.gather(*tasks)
        return list(results)
