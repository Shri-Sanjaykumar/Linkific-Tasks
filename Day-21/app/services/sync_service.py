"""
Day 21 — Synchronous Data Service (Baseline)
Implements blocking file I/O, synchronous network simulation,
direct CPU token normalization, and sequential batch processing.
Used as the verified baseline for scientific performance benchmarking.
"""

import os
import json
import time
import re
from typing import List, Dict, Any, Optional


class SyncDataService:
    """
    Synchronous document search and analytics service.
    All operations execute synchronously on the calling thread.
    """

    def __init__(self, corpus_path: str):
        self.corpus_path = corpus_path
        self._cached_docs: Optional[List[Dict[str, Any]]] = None

    def load_documents(self) -> List[Dict[str, Any]]:
        """Synchronously reads and parses the JSON corpus file using blocking open()."""
        if not os.path.exists(self.corpus_path):
            return []

        # Blocking file read
        with open(self.corpus_path, "r", encoding="utf-8") as f:
            docs = json.load(f)
        return docs

    def _normalize_tokens(self, text: str) -> List[str]:
        """CPU-intensive token extraction and normalization."""
        tokens = re.findall(r"\b[a-zA-Z0-9_-]+\b", text.lower())
        # Simulate slight CPU work (e.g. stemming / token frequency calculation)
        term_freq = {}
        for t in tokens:
            term_freq[t] = term_freq.get(t, 0) + 1
        return [t for t in tokens if len(t) > 2]

    def query(
        self,
        question: str,
        top_k: int = 3,
        category: Optional[str] = None,
        simulate_io_delay: float = 0.04
    ) -> List[Dict[str, Any]]:
        """
        Executes synchronous document retrieval:
        1. Blocking file read (or re-load).
        2. Blocking simulated external I/O delay (time.sleep).
        3. CPU-intensive token scoring.
        4. Category filtering and top-k ranking.
        """
        # 1. Blocking I/O
        docs = self.load_documents()

        # 2. Simulated external I/O (e.g. database query, vector store roundtrip, remote search API)
        if simulate_io_delay > 0:
            time.sleep(simulate_io_delay)

        # 3. CPU token normalization and scoring
        query_terms = set(self._normalize_tokens(question))
        if not query_terms:
            return []

        scored_docs = []
        for doc in docs:
            if category and category.strip() and category.lower() != "string" and doc.get("category", "").lower() != category.lower():
                continue

            doc_terms = set(self._normalize_tokens(doc.get("title", "") + " " + doc.get("content", "")))
            overlap = query_terms.intersection(doc_terms)
            score = round(len(overlap) / max(len(query_terms), 1), 4)

            if score > 0:
                d = dict(doc)
                d["score"] = score
                scored_docs.append(d)

        # 4. Sort by relevance descending
        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        return scored_docs[:top_k]

    def batch_query(
        self,
        questions: List[str],
        top_k: int = 3,
        simulate_io_delay: float = 0.04
    ) -> List[List[Dict[str, Any]]]:
        """
        Processes a batch of queries sequentially in a synchronous for-loop.
        Latency scales linearly with batch size: Total Time ~ N * delay.
        """
        results = []
        for q in questions:
            res = self.query(q, top_k=top_k, simulate_io_delay=simulate_io_delay)
            results.append(res)
        return results
