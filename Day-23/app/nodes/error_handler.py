"""
Day 23: Error Handler Node
Responsibilities:
- Traps unhandled exceptions, validation errors, or missing resources
- Emits diagnostic error messages into the communication log
- Provides safe, non-crashing fallback answers to the user
"""

from typing import Dict, Any
from datetime import datetime, timezone
import logging

from ..schemas import (
    AgentRole,
    MessageType,
    WorkflowStatus,
    AgentMessage
)
from ..state import MultiAgentState

logger = logging.getLogger("LinkificLangGraph.ErrorHandler")


def error_handler_node(state: MultiAgentState) -> Dict[str, Any]:
    """
    Error recovery node providing diagnostic telemetry and safe pipeline termination.
    """
    w_id = state["workflow_id"]
    query = state.get("query", "")
    errors = state.get("errors", ["An unexpected pipeline error occurred."])
    error_summary = "; ".join(errors)

    logger.error("Workflow %s routed to error handler: %s", w_id, error_summary)

    err_msg = AgentMessage(
        correlation_id=w_id,
        sender=AgentRole.ERROR_HANDLER,
        recipient=AgentRole.COORDINATOR,
        message_type=MessageType.ERROR_NOTIFICATION,
        payload={"errors": errors, "query": query},
        summary=f"Error Handler trapped pipeline defect: {error_summary[:100]}"
    )

    final_fallback = (
        f"Unable to complete research request for: '{query}'. "
        f"Encountered pipeline diagnostics: {error_summary}. "
        "Please check your input query or contact system support."
    )

    return {
        "status": WorkflowStatus.FAILED,
        "current_agent": AgentRole.ERROR_HANDLER,
        "final_answer": final_fallback,
        "communication_log": [err_msg],
        "next_step": "end"
    }
