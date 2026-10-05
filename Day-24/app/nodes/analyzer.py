"""
Linkific Enterprise AI Service - Analyzer Agent Node
Responsibilities:
- Synthesize thematic clusters and cross-policy correlations
- Derive structured InsightItems grounded in research findings
- Forward analysis to Critic Agent via ANALYSIS_SUBMISSION
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
    InsightItem,
    AnalysisResult,
    AgentMessage
)
from app.state import MultiAgentState
from app.core.logging_config import get_logger
from app.core.metrics import metrics_registry

logger = get_logger("LinkificService.Analyzer")


def analyzer_node(state: MultiAgentState) -> Dict[str, Any]:
    """
    Groups retrieved evidence into thematic insights and evaluates cross-policy implications.
    """
    metrics_registry.record_agent_node(AgentRole.ANALYZER.value)
    w_id = state["workflow_id"]
    findings = state.get("research_findings")
    now_iso = datetime.now(timezone.utc).isoformat()

    if not findings or not findings.items:
        error_msg = "Analyzer node received empty research findings."
        err_envelope = AgentMessage(
            correlation_id=w_id,
            sender=AgentRole.ANALYZER.value,
            recipient=AgentRole.ERROR_HANDLER.value,
            message_type=MessageType.ERROR_NOTIFICATION,
            payload={"error": error_msg},
            summary="Analyzer flagged missing evidence items."
        )
        logger.error(error_msg)
        return {
            "status": WorkflowStatus.FAILED,
            "errors": [error_msg],
            "communication_log": [err_envelope],
            "next_step": "error_handler"
        }

    # Group evidence by category
    categories: Dict[str, List[Any]] = {}
    for item in findings.items:
        categories.setdefault(item.category, []).append(item)

    insights: List[InsightItem] = []
    thematic_clusters = list(categories.keys())

    for cat, items in categories.items():
        claim_ids = [it.claim_id for it in items]
        summary = f"Category '{cat}' synthesizes {len(items)} policy guidelines: " + " ".join(
            it.excerpt for it in items
        )
        insights.append(
            InsightItem(
                insight_id=f"INS-{uuid.uuid4().hex[:6].upper()}",
                category=cat,
                summary=summary,
                grounding_claims=claim_ids,
                confidence=round(sum(it.relevance_score for it in items) / len(items), 3)
            )
        )

    analysis = AnalysisResult(
        insights=insights,
        thematic_clusters=thematic_clusters,
        overall_confidence=round(sum(ins.confidence for ins in insights) / len(insights), 3)
    )

    analysis_msg = AgentMessage(
        correlation_id=w_id,
        sender=AgentRole.ANALYZER.value,
        recipient=AgentRole.CRITIC.value,
        message_type=MessageType.ANALYSIS_SUBMISSION,
        payload={
            "insight_count": len(insights),
            "thematic_clusters": thematic_clusters,
            "overall_confidence": analysis.overall_confidence
        },
        summary=f"Analyzer synthesized {len(insights)} verified insights across {len(thematic_clusters)} domains."
    )

    # Update Milestone
    updated_milestones = []
    for m in state.get("milestones", []):
        m_step = getattr(m, "step", getattr(m, "step_number", 0))
        m_task = getattr(m, "task", getattr(m, "name", ""))
        if "Cognitive Clustering" in m_task or m_step == 3:
            m_copy = m.model_copy(update={
                "status": "completed",
                "completed_at": now_iso,
                "details": f"Synthesized {len(insights)} insights across clusters: {', '.join(thematic_clusters[:3])}."
            })
            updated_milestones.append(m_copy)

    logger.info(f"Analyzer synthesized {len(insights)} insights for workflow '{w_id}'")

    return {
        "status": WorkflowStatus.ANALYZING,
        "current_agent": AgentRole.CRITIC.value,
        "analysis_result": analysis,
        "milestones": updated_milestones,
        "communication_log": [analysis_msg],
        "next_step": "critic"
    }
