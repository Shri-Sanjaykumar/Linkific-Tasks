"""
Linkific Enterprise AI Service - Error Handler Node
Responsibilities:
- Fallback exception mitigation and circuit breaker isolation
- Error diagnostics formatting and audit event recording
- Graceful termination of failed workflows with diagnostic telemetry
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

logger = get_logger("LinkificService.ErrorHandler")


def error_handler_node(state: MultiAgentState) -> Dict[str, Any]:
    """
    Catches unrecoverable errors and compiles a graceful failure payload.
    """
    metrics_registry.record_agent_node(AgentRole.ERROR_HANDLER.value)
    w_id = state.get("workflow_id", "WF-UNKNOWN")
    errors = state.get("errors", ["Unknown execution anomaly."])
    now_iso = datetime.now(timezone.utc).isoformat()

    diagnostic_summary = f"Workflow failed due to {len(errors)} error(s): " + " | ".join(errors)
    logger.error(f"Error Handler activated for workflow '{w_id}': {diagnostic_summary}")

    fallback_answer = (
        f"The Linkific Enterprise Assistant encountered a processing issue: {errors[0]} "
        "Please verify your query parameters or contact corporate operations."
    )

    err_envelope = AgentMessage(
        correlation_id=w_id,
        sender=AgentRole.ERROR_HANDLER.value,
        recipient="user",
        message_type=MessageType.ERROR_NOTIFICATION,
        payload={
            "errors": errors,
            "failed_at": now_iso,
            "status": "FAILED"
        },
        summary=f"System Error Handler delivered diagnostic notification: {errors[0]}"
    )

    # Mark any pending milestones as failed
    updated_milestones = []
    for m in state.get("milestones", []):
        if m.status != "completed":
            m_copy = m.model_copy(update={
                "status": "failed",
                "completed_at": now_iso,
                "details": f"Terminated by error handler: {errors[0]}"
            })
            updated_milestones.append(m_copy)

    return {
        "status": WorkflowStatus.FAILED,
        "current_agent": AgentRole.ERROR_HANDLER.value,
        "final_answer": fallback_answer,
        "milestones": updated_milestones,
        "communication_log": [err_envelope],
        "next_step": "end"
    }
