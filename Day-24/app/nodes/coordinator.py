"""
Linkific Enterprise AI Service - Coordinator Agent Node
Responsibilities:
- Plan generation & milestone decomposition
- Inter-agent task dispatching via structured AgentMessage
- Final answer synthesis and user-facing delivery
"""

from typing import Dict, Any, List
from datetime import datetime, timezone
import logging

from app.schemas import (
    AgentRole,
    MessageType,
    WorkflowStatus,
    Milestone,
    AgentMessage
)
from app.state import MultiAgentState
from app.core.logging_config import get_logger
from app.core.metrics import metrics_registry

logger = get_logger("LinkificService.Coordinator")


def coordinator_plan(state: MultiAgentState) -> Dict[str, Any]:
    """
    Decomposes the user query into sequential milestones and dispatches
    task assignment to the Research Agent.
    """
    metrics_registry.record_agent_node(AgentRole.COORDINATOR.value)
    w_id = state["workflow_id"]
    query = state.get("query", "").strip()
    mode = state.get("mode", "streamlined")
    now_iso = datetime.now(timezone.utc).isoformat()

    logger.info(f"Coordinator initializing workflow '{w_id}' in '{mode}' mode for query: '{query}'")

    # Input validation guardrail
    if not query or len(query) < 3:
        error_msg = "User query is invalid or too short (< 3 characters)."
        err_envelope = AgentMessage(
            correlation_id=w_id,
            sender=AgentRole.COORDINATOR.value,
            recipient=AgentRole.ERROR_HANDLER.value,
            message_type=MessageType.ERROR_NOTIFICATION,
            payload={"error": error_msg},
            summary="Coordinator flagged invalid query length."
        )
        logger.warning(f"Workflow '{w_id}' rejected due to invalid query: '{query}'")
        return {
            "status": WorkflowStatus.FAILED,
            "errors": [error_msg],
            "communication_log": [err_envelope],
            "next_step": "error_handler"
        }

    # Construct Milestones based on pipeline mode
    if mode == "streamlined":
        milestones = [
            Milestone(
                step=1,
                task="Planning & Task Routing",
                agent=AgentRole.COORDINATOR.value,
                status="completed",
                details="Generated streamlined 4-phase milestone plan.",
                timestamp=now_iso,
                completed_at=now_iso
            ),
            Milestone(
                step=2,
                task="Evidence Retrieval & Grounding",
                agent=AgentRole.RESEARCHER.value,
                status="pending",
                details="Query enterprise documents for grounded policy evidence.",
                timestamp=now_iso
            ),
            Milestone(
                step=3,
                task="Executive Reporting & Citations",
                agent=AgentRole.WRITER.value,
                status="pending",
                details="Synthesize executive brief with grounded citations.",
                timestamp=now_iso
            ),
            Milestone(
                step=4,
                task="Final Answer & Egress Telemetry",
                agent=AgentRole.COORDINATOR.value,
                status="pending",
                details="Assemble consolidated deliverable for client egress.",
                timestamp=now_iso
            )
        ]
    else:
        milestones = [
            Milestone(
                step=1,
                task="Planning & Task Routing",
                agent=AgentRole.COORDINATOR.value,
                status="completed",
                details="Generated comprehensive 6-phase milestone plan.",
                timestamp=now_iso,
                completed_at=now_iso
            ),
            Milestone(
                step=2,
                task="Evidence Retrieval & Grounding",
                agent=AgentRole.RESEARCHER.value,
                status="pending",
                details="Retrieve grounded evidence across enterprise repository.",
                timestamp=now_iso
            ),
            Milestone(
                step=3,
                task="Cognitive Clustering & Insight Derivation",
                agent=AgentRole.ANALYZER.value,
                status="pending",
                details="Perform multi-dimensional synthesis across policy domains.",
                timestamp=now_iso
            ),
            Milestone(
                step=4,
                task="Adversarial Audit & Quality Gate",
                agent=AgentRole.CRITIC.value,
                status="pending",
                details="Verify numeric fidelity, citations, and claim grounding.",
                timestamp=now_iso
            ),
            Milestone(
                step=5,
                task="Executive Reporting & Traceability Matrix",
                agent=AgentRole.WRITER.value,
                status="pending",
                details="Synthesize executive brief with source traceability matrix.",
                timestamp=now_iso
            ),
            Milestone(
                step=6,
                task="Final Answer & Egress Telemetry",
                agent=AgentRole.COORDINATOR.value,
                status="pending",
                details="Assemble final answer deliverable for client egress.",
                timestamp=now_iso
            )
        ]

    task_msg = AgentMessage(
        correlation_id=w_id,
        sender=AgentRole.COORDINATOR.value,
        recipient=AgentRole.RESEARCHER.value,
        message_type=MessageType.TASK_ASSIGNMENT,
        payload={"query": query, "mode": mode, "target_task": "RETRIEVE_EVIDENCE"},
        summary=f"Coordinator assigned research task to Research Agent for inquiry: '{query}'."
    )

    return {
        "status": WorkflowStatus.PLANNING,
        "current_agent": AgentRole.RESEARCHER.value,
        "milestones": milestones,
        "communication_log": [task_msg],
        "next_step": "researcher"
    }


def coordinator_synthesize(state: MultiAgentState) -> Dict[str, Any]:
    """
    Synthesizes the final response from the Writer's report and prepares
    the final client egress deliverable.
    """
    metrics_registry.record_agent_node(AgentRole.COORDINATOR.value)
    w_id = state["workflow_id"]
    query = state.get("query", "")
    writer_report = state.get("final_report")
    critic_reviews = state.get("critic_reviews", [])
    now_iso = datetime.now(timezone.utc).isoformat()

    critic_approved = True
    if critic_reviews:
        critic_approved = (critic_reviews[-1].verdict == "approved")

    # Final Answer Generation
    if writer_report:
        final_answer = (
            f"{writer_report.executive_summary} "
            f"[Sources: {', '.join(writer_report.citations)}]"
        )
    else:
        final_answer = f"Research inquiry '{query}' processed, but no formal report was generated."

    # Mark Final Milestone as Completed
    updated_milestones = []
    for m in state.get("milestones", []):
        m_step = getattr(m, "step", getattr(m, "step_number", 0))
        m_task = getattr(m, "task", getattr(m, "name", ""))
        if "Final Answer" in m_task or m_step in (4, 6):
            m_copy = m.model_copy(update={
                "status": "completed",
                "completed_at": now_iso,
                "details": "Consolidated final answer and report ready for egress."
            })
            updated_milestones.append(m_copy)

    final_msg = AgentMessage(
        correlation_id=w_id,
        sender=AgentRole.COORDINATOR.value,
        recipient="user",
        message_type=MessageType.FINAL_ANSWER,
        payload={
            "final_answer": final_answer,
            "report_id": writer_report.report_id if writer_report else None,
            "critic_approved": critic_approved
        },
        summary=f"Coordinator delivered verified answer to user with {len(updated_milestones)} milestones completed."
    )

    logger.info(f"Coordinator successfully finalized workflow '{w_id}'")

    return {
        "status": WorkflowStatus.COMPLETED,
        "current_agent": AgentRole.COORDINATOR.value,
        "final_answer": final_answer,
        "milestones": updated_milestones,
        "communication_log": [final_msg],
        "next_step": "end"
    }
