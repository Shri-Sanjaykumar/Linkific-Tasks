"""
Linkific Enterprise AI Service - Writer Agent Node
Responsibilities:
- Synthesize executive intelligence briefs grounded in evidence
- Build section-by-section narratives with explicit source citations
- Construct evidence-to-source traceability matrix
- Submit REPORT_DRAFT message to Coordinator Agent
"""

from typing import Dict, Any, List
from datetime import datetime, timezone
import uuid
import logging

from app.schemas import (
    AgentRole,
    MessageType,
    WorkflowStatus,
    Milestone,
    WriterReport,
    AgentMessage
)
from app.state import MultiAgentState
from app.core.logging_config import get_logger
from app.core.metrics import metrics_registry

logger = get_logger("LinkificService.Writer")


def writer_node(state: MultiAgentState) -> Dict[str, Any]:
    """
    Assembles grounded evidence and analysis into an executive report.
    """
    metrics_registry.record_agent_node(AgentRole.WRITER.value)
    w_id = state["workflow_id"]
    query = state.get("query", "")
    mode = state.get("mode", "streamlined")
    findings = state.get("research_findings")
    analysis = state.get("analysis_result")
    now_iso = datetime.now(timezone.utc).isoformat()

    report_id = f"REP-{uuid.uuid4().hex[:6].upper()}"

    # Build Sections and Traceability
    sections: Dict[str, str] = {}
    evidence_matrix: Dict[str, List[str]] = {}
    citations: List[str] = []

    if findings and findings.items:
        for item in findings.items:
            sec_title = f"Policy Dimensions: {item.category}"
            sections[sec_title] = f"- {item.excerpt} [{item.doc_id}]"
            evidence_matrix[item.claim_id] = [item.doc_id]
            if item.doc_id not in citations:
                citations.append(item.doc_id)

    # Executive Summary Construction
    summary_parts = [
        f"This verified enterprise brief addresses the inquiry: '{query}'."
    ]
    if findings and findings.items:
        for it in findings.items[:2]:
            summary_parts.append(f"According to {it.category} guidelines ({it.doc_id}), {it.excerpt}")

    exec_summary = " ".join(summary_parts)

    strategic_recs = [
        "Ensure cross-departmental alignment prior to executing major policy changes.",
        "Maintain audit logging compliance for all operations intersecting user data or infrastructure.",
        "Subject critical procedural revisions to periodic adversarial review."
    ]

    report = WriterReport(
        report_id=report_id,
        title=f"Enterprise Intelligence Brief: {query[:80]}",
        executive_summary=exec_summary,
        sections=sections,
        evidence_matrix=evidence_matrix,
        strategic_recommendations=strategic_recs,
        citations=citations
    )

    report_msg = AgentMessage(
        correlation_id=w_id,
        sender=AgentRole.WRITER.value,
        recipient=AgentRole.COORDINATOR.value,
        message_type=MessageType.REPORT_DRAFT,
        payload={
            "report_id": report_id,
            "section_count": len(sections),
            "citations": citations
        },
        summary=f"Writer Agent synthesized executive report ({report_id}) with {len(sections)} sections."
    )

    # Update Milestone
    updated_milestones = []
    for m in state.get("milestones", []):
        m_step = getattr(m, "step", getattr(m, "step_number", 0))
        m_task = getattr(m, "task", getattr(m, "name", ""))
        if "Executive Reporting" in m_task or m_step in (3, 5):
            m_copy = m.model_copy(update={
                "status": "completed",
                "completed_at": now_iso,
                "details": f"Generated executive report {report_id} with {len(sections)} sections."
            })
            updated_milestones.append(m_copy)

    logger.info(f"Writer generated report '{report_id}' for workflow '{w_id}'")

    return {
        "status": WorkflowStatus.WRITING,
        "current_agent": AgentRole.COORDINATOR.value,
        "final_report": report,
        "milestones": updated_milestones,
        "communication_log": [report_msg],
        "next_step": "coordinator_synthesize"
    }
