"""
Day 21 — Tests for Service Layer & Functional Parity (Sync vs Async)
"""

import pytest
from app.config import settings
from app.services.sync_service import SyncDataService
from app.services.async_service import AsyncDataService


def test_sync_service_query():
    """Verify SyncDataService executes retrieval and scoring."""
    service = SyncDataService(corpus_path=settings.CORPUS_FILE)
    docs = service.load_documents()
    assert len(docs) > 0

    results = service.query("leave and attendance policy", top_k=2, simulate_io_delay=0.0)
    assert len(results) > 0
    assert results[0]["id"] == "DOC-POL-001"
    assert results[0]["score"] > 0.0


@pytest.mark.anyio
async def test_async_service_query():
    """Verify AsyncDataService executes retrieval and scoring asynchronously."""
    service = AsyncDataService(corpus_path=settings.CORPUS_FILE)
    docs = await service.load_documents_async()
    assert len(docs) > 0

    results = await service.query_async("leave and attendance policy", top_k=2, simulate_io_delay=0.0)
    assert len(results) > 0
    assert results[0]["id"] == "DOC-POL-001"
    assert results[0]["score"] > 0.0


@pytest.mark.anyio
async def test_service_functional_parity():
    """
    CRITICAL FAIRNESS TEST: Verify that SyncDataService and AsyncDataService
    produce IDENTICAL ranked documents and relevance scores on identical queries.
    """
    sync_svc = SyncDataService(corpus_path=settings.CORPUS_FILE)
    async_svc = AsyncDataService(corpus_path=settings.CORPUS_FILE)

    test_queries = [
        "leave and core collaboration hours",
        "remote hardware security guidelines",
        "engineering onboarding code review",
        "data privacy and compliance standard"
    ]

    for q in test_queries:
        sync_res = sync_svc.query(q, top_k=3, simulate_io_delay=0.0)
        async_res = await async_svc.query_async(q, top_k=3, simulate_io_delay=0.0)

        assert len(sync_res) == len(async_res), f"Result count mismatch on query '{q}'"
        for s_doc, a_doc in zip(sync_res, async_res):
            assert s_doc["id"] == a_doc["id"], f"Document ID mismatch on query '{q}'"
            assert s_doc["score"] == a_doc["score"], f"Score mismatch on query '{q}'"
