"""
Day 23: Coordinator Agent Node
Responsibilities:
- Plan generation & milestone decomposition
- Inter-agent task dispatching via structured AgentMessage
- Final answer synthesis and user-facing delivery
"""

from typing import Dict, Any, List
from datetime import datetime, timezone
import logging

from ..schemas import (
    AgentRole,
    MessageType,
    WorkflowStatus,
    Milestone,
    AgentMessage
)
from ..state import MultiAgentState

logger = logging.getLogger("LinkificLangGraph.Coordinator")


def coordinator_plan(state: MultiAgentState) -> Dict[str, Any]:
    """
    Decomposes the user query into sequential milestones and dispatches
    task assignment to the Research Agent.
    """
    w_id = state["workflow_id"]
    query = state.get("query", "").strip()
    mode = state.get("mode", "streamlined")
    now_iso = datetime.now(timezone.utc).isoformat()

    # Input validation guardrail
    if not query or len(query) < 3:
        error_msg = "User query is invalid or too short (< 3 characters)."
        err_envelope = AgentMessage(
            correlation_id=w_id,
            sender=AgentRole.COORDINATOR,
            recipient=AgentRole.ERROR_HANDLER,
            message_type=MessageType.ERROR_NOTIFICATION,
            payload={"error": error_msg},
            summary="Coordinator flagged invalid query length."
        )
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
                step_number=1,
                name="Planning & Task Routing",
                assigned_agent=AgentRole.COORDINATOR,
                status="completed",
                description="Decompose user inquiry and establish execution topology.",
                started_at=now_iso,
                completed_at=now_iso
            ),
            Milestone(
                step_number=2,
                name="Evidence Retrieval & Grounding",
                assigned_agent=AgentRole.RESEARCH,
                status="in_progress",
                description="Retrieve grounded evidence chunks from enterprise corpus.",
                started_at=now_iso
            ),
            Milestone(
                step_number=3,
                name="Executive Reporting & Citations",
                assigned_agent=AgentRole.WRITER,
                status="pending",
                description="Synthesize verified findings into executive brief with citations."
            ),
            Milestone(
                step_number=4,
                name="Final Answer & Egress Telemetry",
                assigned_agent=AgentRole.COORDINATOR,
                status="pending",
                description="Validate report deliverables and emit final response to user."
            )
        ]
    else:  # comprehensive mode
        milestones = [
            Milestone(
                step_number=1,
                name="Planning & Task Routing",
                assigned_agent=AgentRole.COORDINATOR,
                status="completed",
                description="Decompose research inquiry into 6 execution milestones.",
                started_at=now_iso,
                completed_at=now_iso
            ),
            Milestone(
                step_number=2,
                name="Evidence Retrieval & Grounding",
                assigned_agent=AgentRole.RESEARCH,
                status="in_progress",
                description="Search enterprise policy repository with exact provenance.",
                started_at=now_iso
            ),
            Milestone(
                step_number=3,
                name="Cognitive Clustering & Insight Derivation",
                assigned_agent=AgentRole.ANALYZER,
                status="pending",
                description="Derive structured insights, correlations, and gap analyses."
            ),
            Milestone(
                step_number=4,
                name="Adversarial Audit & Quality Gate",
                assigned_agent=AgentRole.CRITIC,
                status="pending",
                description="Verify citation coverage, grounding, and numerical accuracy."
            ),
            Milestone(
                step_number=5,
                name="Executive Reporting & Traceability Matrix",
                assigned_agent=AgentRole.WRITER,
                status="pending",
                description="Synthesize audited insights into formal intelligence brief."
            ),
            Milestone(
                step_number=6,
                name="Final Answer & Egress Telemetry",
                assigned_agent=AgentRole.COORDINATOR,
                status="pending",
                description="Verify final response against original user brief and terminate."
            )
        ]

    # Task Assignment Message to Research Agent
    dispatch_msg = AgentMessage(
        correlation_id=w_id,
        sender=AgentRole.COORDINATOR,
        recipient=AgentRole.RESEARCH,
        message_type=MessageType.TASK_ASSIGNMENT,
        payload={
            "query": query,
            "mode": mode,
            "target_task": "RETRIEVE_EVIDENCE"
        },
        summary=f"Coordinator assigned research task to Research Agent for inquiry: '{query}'."
    )

    return {
        "status": WorkflowStatus.PLANNING,
        "current_agent": AgentRole.COORDINATOR,
        "milestones": milestones,
        "communication_log": [dispatch_msg],
        "next_step": "researcher"
    }


def coordinator_synthesize(state: MultiAgentState) -> Dict[str, Any]:
    """
    Final node evaluating report deliverables, formatting the executive answer,
    and emitting the final response message to the user.
    """
    w_id = state["workflow_id"]
    query = state.get("query", "")
    report = state.get("final_report")
    now_iso = datetime.now(timezone.utc).isoformat()

    # Formulate final answer text
    if report and report.executive_summary:
        summary_core = report.executive_summary
        citations = []
        for sec in report.sections:
            citations.extend(sec.cited_sources)
        unique_cites = sorted(list(set(citations)))
        cites_suffix = f" [Sources: {', '.join(unique_cites)}]" if unique_cites else ""
        final_answer = f"{summary_core}{cites_suffix}"
    else:
        final_answer = f"Research inquiry '{query}' was processed. No definitive documentation was identified."

    # Final Milestone Update
    final_milestones = []
    for m in state.get("milestones", []):
        if m.assigned_agent == AgentRole.COORDINATOR and m.name.startswith("Final"):
            m.status = "completed"
            m.completed_at = now_iso
            final_milestones.append(m)

    # Final Answer Message to User
    answer_msg = AgentMessage(
        correlation_id=w_id,
        sender=AgentRole.COORDINATOR,
        recipient=AgentRole.USER,
        message_type=MessageType.FINAL_ANSWER,
        payload={
            "final_answer": final_answer,
            "report_id": report.report_id if report else None,
            "critic_approved": True if not state.get("critic_reviews") or state["critic_reviews"][-1].verdict == "approved" else False
        },
        summary=f"Coordinator delivered verified answer to user with {len(final_milestones)} milestones completed."
    )

    return {
        "status": WorkflowStatus.COMPLETED,
        "current_agent": AgentRole.COORDINATOR,
        "final_answer": final_answer,
        "milestones": final_milestones,
        "communication_log": [answer_msg],
        "next_step": "end"
    }


# Node aliases for consistent naming
coordinator_plan_node = coordinator_plan
coordinator_synthesize_node = coordinator_synthesize
