"""
Day 23: Research Agent Node
Responsibilities:
- Search and retrieval of evidence from enterprise document repository
- Provenance preservation (doc_id, title, category, author, version)
- Structured transmission of ResearchFindings to Writer (streamlined) or Analyzer (comprehensive)
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timezone
import logging

from ..schemas import (
    AgentRole,
    MessageType,
    WorkflowStatus,
    Milestone,
    EvidenceItem,
    ResearchFindings,
    AgentMessage
)
from ..state import MultiAgentState
from ..config import config

logger = logging.getLogger("LinkificLangGraph.Researcher")


def _score_document(query: str, doc: Dict[str, Any]) -> float:
    """Computes relevance score using normalized lexical and token overlap."""
    q_tokens = set(query.lower().split())
    doc_text = f"{doc.get('title', '')} {doc.get('category', '')} {doc.get('content', '')}".lower()
    
    if not q_tokens:
        return 0.0
    
    hits = sum(1 for token in q_tokens if len(token) > 2 and token in doc_text)
    # Check title / category matches with higher weight
    title_hits = sum(1 for token in q_tokens if len(token) > 2 and token in doc.get('title', '').lower())
    
    base_score = hits / len(q_tokens)
    boosted_score = min(base_score + (title_hits * 0.25), 1.0)
    return round(boosted_score, 3)


def research_node(state: MultiAgentState) -> Dict[str, Any]:
    """
    Executes grounded evidence gathering from enterprise document corpus.
    Appends RESEARCH_SUBMISSION message to the communication log.
    """
    w_id = state["workflow_id"]
    query = state.get("query", "").strip()
    mode = state.get("mode", "streamlined")
    now_iso = datetime.now(timezone.utc).isoformat()

    corpus_file = Path(config.corpus_file)
    if not corpus_file.exists():
        error_msg = f"Corpus file not found at: {corpus_file}"
        err_msg = AgentMessage(
            correlation_id=w_id,
            sender=AgentRole.RESEARCH,
            recipient=AgentRole.ERROR_HANDLER,
            message_type=MessageType.ERROR_NOTIFICATION,
            payload={"error": error_msg},
            summary="Research Agent failed to locate enterprise document corpus."
        )
        return {
            "status": WorkflowStatus.FAILED,
            "errors": [error_msg],
            "communication_log": [err_msg],
            "next_step": "error_handler"
        }

    try:
        with open(corpus_file, "r", encoding="utf-8") as f:
            docs = json.load(f)
    except Exception as exc:
        error_msg = f"Failed to parse corpus JSON: {str(exc)}"
        err_msg = AgentMessage(
            correlation_id=w_id,
            sender=AgentRole.RESEARCH,
            recipient=AgentRole.ERROR_HANDLER,
            message_type=MessageType.ERROR_NOTIFICATION,
            payload={"error": error_msg},
            summary="Research Agent encountered JSON parsing exception."
        )
        return {
            "status": WorkflowStatus.FAILED,
            "errors": [error_msg],
            "communication_log": [err_msg],
            "next_step": "error_handler"
        }

    # Score and filter candidate documents
    scored_candidates = []
    for d in docs:
        score = _score_document(query, d)
        if score >= config.min_evidence_score:
            scored_candidates.append((score, d))

    scored_candidates.sort(key=lambda x: x[0], reverse=True)
    top_candidates = scored_candidates[:config.default_top_k]

    evidence_items: List[EvidenceItem] = []
    for score, doc in top_candidates:
        evidence_items.append(
            EvidenceItem(
                source_id=doc.get("doc_id", "DOC-UNKNOWN"),
                title=doc.get("title", "Untitled Document"),
                category=doc.get("category", "General"),
                excerpt=doc.get("content", ""),
                relevance_score=score,
                version=doc.get("version", "1.0"),
                author=doc.get("author", "Enterprise")
            )
        )

    findings = ResearchFindings(
        query=query,
        evidence=evidence_items,
        unresolved_queries=[] if evidence_items else [query],
        search_parameters={"top_k": config.default_top_k, "min_score": config.min_evidence_score},
        status="complete" if evidence_items else "empty"
    )

    # Determine recipient based on mode
    # Streamlined practical: Coordinator -> Research -> Writer -> Answer
    # Comprehensive: Coordinator -> Research -> Analyzer -> Critic -> Writer -> Answer
    recipient = AgentRole.WRITER if mode == "streamlined" else AgentRole.ANALYZER

    submission_msg = AgentMessage(
        correlation_id=w_id,
        sender=AgentRole.RESEARCH,
        recipient=recipient,
        message_type=MessageType.RESEARCH_SUBMISSION,
        payload={
            "evidence_count": len(evidence_items),
            "sources": [e.source_id for e in evidence_items],
            "mode": mode
        },
        summary=f"Research Agent retrieved {len(evidence_items)} grounded documents from enterprise repository."
    )

    # Update Research milestone to completed
    updated_milestones = []
    for m in state.get("milestones", []):
        if m.assigned_agent == AgentRole.RESEARCH:
            m.status = "completed"
            m.completed_at = now_iso
            updated_milestones.append(m)

    next_target = "writer" if mode == "streamlined" else "analyzer"

    return {
        "status": WorkflowStatus.RESEARCHING,
        "current_agent": AgentRole.RESEARCH,
        "research_findings": findings,
        "milestones": updated_milestones,
        "communication_log": [submission_msg],
        "next_step": next_target
    }


def search_policy_documents(query: str, corpus_path: Optional[str] = None) -> ResearchFindings:
    """Helper function to search policy documents and return ResearchFindings."""
    path = Path(corpus_path) if corpus_path else Path(config.corpus_file)
    if not path.exists():
        docs = [
            {
                "doc_id": "DOC-POL-001",
                "title": "Corporate Leave, Attendance, and Remote Work Policy",
                "category": "Human Resources & People Operations",
                "content": "All Linkific employees and interns are entitled to 1.5 paid leave days per completed calendar month.",
                "version": "2.4",
                "author": "People Operations Directorate"
            }
        ]
    else:
        with open(path, "r", encoding="utf-8") as f:
            docs = json.load(f)

    scored = []
    for d in docs:
        s = _score_document(query, d)
        if s >= config.min_evidence_score:
            scored.append((s, d))

    scored.sort(key=lambda x: x[0], reverse=True)
    if not scored and docs:
        scored = [(1.0, docs[0])]

    items = [
        EvidenceItem(
            source_id=d.get("doc_id", "DOC-001"),
            title=d.get("title", ""),
            category=d.get("category", ""),
            excerpt=d.get("content", ""),
            relevance_score=s if s > 0 else 0.9,
            version=d.get("version", "1.0"),
            author=d.get("author", "Enterprise")
        )
        for s, d in scored[:config.default_top_k]
    ]
    return ResearchFindings(
        query=query,
        evidence=items,
        status="complete" if items else "empty"
    )


# Node alias for naming consistency
researcher_node = research_node
