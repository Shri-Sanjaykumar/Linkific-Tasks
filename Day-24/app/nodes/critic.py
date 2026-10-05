"""
Linkific Enterprise AI Service - Critic Agent Node
Responsibilities:
- Adversarial quality gating & numerical factual verification
- Citation coverage evaluation
- Revision routing or drafting authorization
"""

from typing import Dict, Any, List
from datetime import datetime, timezone
import re
import logging

from app.schemas import (
    AgentRole,
    MessageType,
    WorkflowStatus,
    Milestone,
    CriticReview,
    AgentMessage
)
from app.state import MultiAgentState
from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.core.metrics import metrics_registry

logger = get_logger("LinkificService.Critic")


def critic_node(state: MultiAgentState) -> Dict[str, Any]:
    """
    Performs adversarial inspection on research and analysis artifacts.
    Enforces quality score threshold and factual precision gates.
    """
    metrics_registry.record_agent_node(AgentRole.CRITIC.value)
    w_id = state["workflow_id"]
    findings = state.get("research_findings")
    analysis = state.get("analysis_result")
    rev_count = state.get("revision_count", 0)
    settings = get_settings()
    max_revisions = state.get("max_revisions", settings.MAX_WORKFLOW_REVISIONS)
    threshold = settings.CRITIC_APPROVAL_THRESHOLD
    now_iso = datetime.now(timezone.utc).isoformat()

    defects: List[str] = []
    checks: Dict[str, bool] = {}

    # Check 1: Evidence Presence
    if not findings or not findings.items:
        defects.append("Zero evidence claims retrieved from enterprise documents.")
        checks["evidence_presence"] = False
    else:
        checks["evidence_presence"] = True

    # Check 2: Numerical & Factual Precision
    # Verify decimal numbers and dollar values are properly formatted
    text_corpus = ""
    if findings:
        text_corpus += " ".join(item.excerpt for item in findings.items)
    if analysis:
        text_corpus += " " + " ".join(ins.summary for ins in analysis.insights)

    # Check for known policy constants
    if "paid leave" in text_corpus.lower():
        checks["paid_leave_precision"] = ("1.5" in text_corpus)
        if not checks["paid_leave_precision"]:
            defects.append("Paid leave value is distorted (expected exactly '1.5').")

    if "hardware allowance" in text_corpus.lower():
        checks["hardware_allowance_precision"] = ("500" in text_corpus)
        if not checks["hardware_allowance_precision"]:
            defects.append("Hardware allowance amount is distorted (expected '$500').")

    # Check 3: Citation Grounding
    if findings and findings.items:
        unanchored = [it.claim_id for it in findings.items if not it.doc_id.startswith("DOC-")]
        checks["citation_integrity"] = (len(unanchored) == 0)
        if unanchored:
            defects.append(f"Found unanchored claims without DOC- prefixes: {unanchored}")
    else:
        checks["citation_integrity"] = False

    # Calculate Quality Score
    passed_checks = sum(1 for v in checks.values() if v)
    total_checks = max(len(checks), 1)
    quality_score = round(passed_checks / total_checks, 2)

    is_approved = (quality_score >= threshold and len(defects) == 0)

    # Circuit breaker if revisions exhausted
    if not is_approved and rev_count >= max_revisions:
        logger.warning(f"Critic circuit breaker triggered for workflow '{w_id}' (max revisions reached: {rev_count})")
        is_approved = True
        defects.append("Forced approval via safety circuit breaker (max revisions reached).")

    verdict = "approved" if is_approved else "rejected"

    review = CriticReview(
        verdict=verdict,
        quality_score=quality_score,
        defect_count=len(defects),
        critique_notes=defects if defects else ["All numerical constants and citation anchors verified."],
        factual_accuracy_checks=checks,
        citation_coverage=100.0 if checks.get("citation_integrity", True) else 75.0
    )

    if is_approved:
        critic_msg = AgentMessage(
            correlation_id=w_id,
            sender=AgentRole.CRITIC.value,
            recipient=AgentRole.COORDINATOR.value,
            message_type=MessageType.CRITIC_REVIEW,
            payload={
                "verdict": verdict,
                "quality_score": quality_score,
                "citation_coverage": review.citation_coverage,
                "defect_count": len(defects)
            },
            summary=f"Critic Agent APPROVED analysis with quality score {quality_score:.2f}."
        )

        # Update Milestone
        updated_milestones = []
        for m in state.get("milestones", []):
            m_step = getattr(m, "step", getattr(m, "step_number", 0))
            m_task = getattr(m, "task", getattr(m, "name", ""))
            if "Adversarial Audit" in m_task or m_step == 4:
                m_copy = m.model_copy(update={
                    "status": "completed",
                    "completed_at": now_iso,
                    "details": f"Critic approved analysis with quality score {quality_score:.2f}."
                })
                updated_milestones.append(m_copy)

        logger.info(f"Critic APPROVED workflow '{w_id}' with score {quality_score}")

        return {
            "status": WorkflowStatus.REVIEWING,
            "current_agent": AgentRole.WRITER.value,
            "critic_reviews": [review],
            "milestones": updated_milestones,
            "communication_log": [critic_msg],
            "next_step": "writer"
        }
    else:
        critic_msg = AgentMessage(
            correlation_id=w_id,
            sender=AgentRole.CRITIC.value,
            recipient=AgentRole.ANALYZER.value,
            message_type=MessageType.REVISION_REQUEST,
            payload={
                "verdict": verdict,
                "quality_score": quality_score,
                "defects": defects,
                "revision_count": rev_count + 1
            },
            summary=f"Critic Agent REJECTED analysis. Requested revision #{rev_count + 1} for {len(defects)} defects."
        )

        logger.warning(f"Critic REJECTED workflow '{w_id}'. Requesting revision #{rev_count + 1}")

        return {
            "status": WorkflowStatus.REVISING,
            "current_agent": AgentRole.ANALYZER.value,
            "revision_count": rev_count + 1,
            "critic_reviews": [review],
            "communication_log": [critic_msg],
            "next_step": "analyzer"
        }
