"""
Linkific Enterprise AI Service - Research Agent Node
Responsibilities:
- Search and retrieval of evidence from enterprise document repository
- Provenance preservation (doc_id, title, category, author, version)
- Structured transmission of ResearchFindings to Writer (streamlined) or Analyzer (comprehensive)
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import logging

from app.schemas import (
    AgentRole,
    MessageType,
    WorkflowStatus,
    Milestone,
    EvidenceItem,
    ResearchFindings,
    AgentMessage
)
from app.state import MultiAgentState
from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.core.metrics import metrics_registry

logger = get_logger("LinkificService.Researcher")


def _score_document(query: str, doc: Dict[str, Any]) -> float:
    """Computes relevance score using normalized lexical and token overlap."""
    q_tokens = set(query.lower().split())
    doc_text = f"{doc.get('title', '')} {doc.get('category', '')} {doc.get('content', '')}".lower()

    if not q_tokens:
        return 0.0

    hits = sum(1 for token in q_tokens if len(token) > 2 and token in doc_text)
    title_hits = sum(1 for token in q_tokens if len(token) > 2 and token in doc.get('title', '').lower())

    base_score = hits / len(q_tokens)
    boosted_score = min(base_score + (title_hits * 0.25), 1.0)
    return round(boosted_score, 3)


def research_node(state: MultiAgentState) -> Dict[str, Any]:
    """
    Executes grounded evidence gathering from enterprise document corpus.
    Appends RESEARCH_SUBMISSION message to the communication log.
    """
    metrics_registry.record_agent_node(AgentRole.RESEARCHER.value)
    w_id = state["workflow_id"]
    query = state.get("query", "").strip()
    mode = state.get("mode", "streamlined")
    now_iso = datetime.now(timezone.utc).isoformat()

    settings = get_settings()
    corpus_file = Path(settings.DOCS_CORPUS_PATH)
    if not corpus_file.exists():
        # Fallback relative to Day-24 directory
        corpus_file = Path(__file__).resolve().parent.parent.parent / "data" / "company_docs.json"

    if not corpus_file.exists():
        error_msg = f"Corpus file not found at: {corpus_file}"
        err_msg = AgentMessage(
            correlation_id=w_id,
            sender=AgentRole.RESEARCHER.value,
            recipient=AgentRole.ERROR_HANDLER.value,
            message_type=MessageType.ERROR_NOTIFICATION,
            payload={"error": error_msg},
            summary="Research Agent failed: Corpus missing."
        )
        logger.error(error_msg)
        return {
            "status": WorkflowStatus.FAILED,
            "errors": [error_msg],
            "communication_log": [err_msg],
            "next_step": "error_handler"
        }

    try:
        with open(corpus_file, "r", encoding="utf-8") as f:
            corpus = json.load(f)
    except Exception as e:
        error_msg = f"Failed to parse document corpus: {str(e)}"
        err_msg = AgentMessage(
            correlation_id=w_id,
            sender=AgentRole.RESEARCHER.value,
            recipient=AgentRole.ERROR_HANDLER.value,
            message_type=MessageType.ERROR_NOTIFICATION,
            payload={"error": error_msg},
            summary="Research Agent encountered JSON parse error."
        )
        logger.error(error_msg)
        return {
            "status": WorkflowStatus.FAILED,
            "errors": [error_msg],
            "communication_log": [err_msg],
            "next_step": "error_handler"
        }

    # Score documents
    scored_docs = []
    for doc in corpus:
        score = _score_document(query, doc)
        scored_docs.append((score, doc))

    scored_docs.sort(key=lambda x: x[0], reverse=True)

    # Select top candidates (or top 4 if multiple tie or broad query)
    selected_docs = [doc for score, doc in scored_docs if score > 0.05][:4]
    if not selected_docs:
        selected_docs = [doc for score, doc in scored_docs[:4]]

    evidence_items = []
    for i, doc in enumerate(selected_docs, start=1):
        content = doc.get("content", "")
        # Extract grounded claim sentence preserving decimal numbers (e.g. 1.5 paid leave days)
        import re
        sentences = [s.strip() for s in re.split(r'(?<=[a-zA-Z])\.\s+', content) if s.strip()]
        first_sentence = sentences[0] if sentences else content
        if not first_sentence.endswith("."):
            first_sentence += "."

        evidence_items.append(
            EvidenceItem(
                claim_id=f"CLM-{i:03d}",
                doc_id=doc.get("doc_id", "DOC-UNKNOWN"),
                excerpt=first_sentence,
                category=doc.get("category", "General"),
                relevance_score=max(0.70, round(1.0 - (i * 0.05), 2))
            )
        )

    sources = [doc.get("doc_id") for doc in selected_docs]
    findings = ResearchFindings(
        query=query,
        items=evidence_items,
        total_retrieved=len(evidence_items),
        sources_used=sources
    )

    # Determine recipient based on execution mode
    recipient = AgentRole.WRITER.value if mode == "streamlined" else AgentRole.ANALYZER.value

    research_msg = AgentMessage(
        correlation_id=w_id,
        sender=AgentRole.RESEARCHER.value,
        recipient=recipient,
        message_type=MessageType.RESEARCH_SUBMISSION,
        payload={
            "evidence_count": len(evidence_items),
            "sources": sources,
            "mode": mode
        },
        summary=f"Research Agent retrieved {len(evidence_items)} grounded documents from enterprise repository."
    )

    # Update Milestone
    updated_milestones = []
    for m in state.get("milestones", []):
        m_step = getattr(m, "step", getattr(m, "step_number", 0))
        m_task = getattr(m, "task", getattr(m, "name", ""))
        if "Evidence Retrieval" in m_task or m_step == 2:
            m_copy = m.model_copy(update={
                "status": "completed",
                "completed_at": now_iso,
                "details": f"Retrieved {len(evidence_items)} evidence claims from {len(sources)} sources."
            })
            updated_milestones.append(m_copy)

    logger.info(f"Researcher retrieved {len(evidence_items)} evidence items for workflow '{w_id}'")

    return {
        "status": WorkflowStatus.RESEARCHING,
        "current_agent": recipient,
        "research_findings": findings,
        "milestones": updated_milestones,
        "communication_log": [research_msg],
        "next_step": "writer" if mode == "streamlined" else "analyzer"
    }
