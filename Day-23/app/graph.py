"""
Day 23: LangGraph Multi-Agent StateGraph Architecture
Linkific Enterprise Multi-Agent Research Assistant
"""

import time
from typing import Optional, Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.base import BaseCheckpointSaver

from .state import MultiAgentState, create_initial_state
from .schemas import WorkflowRequest, WorkflowResponse, WorkflowStatus
from .nodes.coordinator import coordinator_plan, coordinator_synthesize
from .nodes.researcher import research_node
from .nodes.analyzer import analyzer_node
from .nodes.critic import critic_node
from .nodes.writer import writer_node
from .nodes.error_handler import error_handler_node


def _route_after_coordinator_plan(state: MultiAgentState) -> str:
    """Routes to error handler if validation fails, otherwise proceeds to research."""
    if state.get("next_step") == "error_handler" or state.get("errors"):
        return "error_handler"
    return "researcher"


def _route_after_research(state: MultiAgentState) -> str:
    """Routes based on workflow mode: streamlined to writer, comprehensive to analyzer."""
    if state.get("next_step") == "error_handler" or state.get("errors"):
        return "error_handler"
    mode = state.get("mode", "streamlined")
    if mode == "streamlined":
        return "writer"
    return "analyzer"


def _route_after_critic(state: MultiAgentState) -> str:
    """Evaluates Critic verdict: loops back to analyzer if revision required, else writer."""
    if state.get("next_step") == "error_handler":
        return "error_handler"
    if state.get("next_step") == "analyzer":
        return "analyzer"
    return "writer"


def _route_after_writer(state: MultiAgentState) -> str:
    """Routes writer draft to coordinator synthesis."""
    if state.get("next_step") == "error_handler":
        return "error_handler"
    return "coordinator_synthesize"


def build_multi_agent_graph(
    checkpointer: Optional[BaseCheckpointSaver] = None
):
    """
    Constructs and compiles the unified LangGraph StateGraph.
    Dynamically routes between Streamlined (Practical) and Comprehensive modes.
    """
    builder = StateGraph(MultiAgentState)

    # 1. Register Nodes
    builder.add_node("coordinator_plan", coordinator_plan)
    builder.add_node("researcher", research_node)
    builder.add_node("analyzer", analyzer_node)
    builder.add_node("critic", critic_node)
    builder.add_node("writer", writer_node)
    builder.add_node("coordinator_synthesize", coordinator_synthesize)
    builder.add_node("error_handler", error_handler_node)

    # 2. Add Ingress Edge
    builder.add_edge(START, "coordinator_plan")

    # 3. Add Conditional Routing Edges
    builder.add_conditional_edges(
        "coordinator_plan",
        _route_after_coordinator_plan,
        {
            "researcher": "researcher",
            "error_handler": "error_handler"
        }
    )

    builder.add_conditional_edges(
        "researcher",
        _route_after_research,
        {
            "writer": "writer",
            "analyzer": "analyzer",
            "error_handler": "error_handler"
        }
    )

    builder.add_edge("analyzer", "critic")

    builder.add_conditional_edges(
        "critic",
        _route_after_critic,
        {
            "writer": "writer",
            "analyzer": "analyzer",
            "error_handler": "error_handler"
        }
    )

    builder.add_conditional_edges(
        "writer",
        _route_after_writer,
        {
            "coordinator_synthesize": "coordinator_synthesize",
            "error_handler": "error_handler"
        }
    )

    builder.add_edge("coordinator_synthesize", END)
    builder.add_edge("error_handler", END)

    # 4. Compile Graph
    if checkpointer is not None:
        return builder.compile(checkpointer=checkpointer)
    return builder.compile()


class MultiAgentWorkflowEngine:
    """
    High-level facade executing the compiled LangGraph workflow.
    Converts client requests into state and returns validated responses.
    """

    def __init__(self, checkpointer: Optional[BaseCheckpointSaver] = None):
        self.checkpointer = checkpointer
        self.app = build_multi_agent_graph(checkpointer=checkpointer)

    def execute(self, request: WorkflowRequest) -> WorkflowResponse:
        """
        Executes end-to-end multi-agent workflow synchronously.
        """
        start_time = time.time()
        initial_state = create_initial_state(
            query=request.query,
            mode=request.mode,
            max_revisions=request.max_revisions
        )

        config_dict = {}
        if self.checkpointer is not None:
            config_dict = {"configurable": {"thread_id": initial_state["workflow_id"]}}

        # Invoke LangGraph application
        final_state = self.app.invoke(initial_state, config=config_dict if config_dict else None)
        elapsed = round(time.time() - start_time, 3)

        # Build WorkflowResponse
        status = final_state.get("status", WorkflowStatus.COMPLETED)
        final_answer = final_state.get("final_answer", "")
        report = final_state.get("final_report")
        critic_approved = True
        if final_state.get("critic_reviews"):
            critic_approved = (final_state["critic_reviews"][-1].verdict == "approved")

        return WorkflowResponse(
            workflow_id=final_state["workflow_id"],
            query=final_state["query"],
            status=status,
            final_answer=final_answer,
            executive_report=report,
            critic_approved=critic_approved,
            milestones=final_state.get("milestones", []),
            communication_log=final_state.get("communication_log", []),
            execution_time_seconds=elapsed,
            errors=final_state.get("errors", [])
        )
