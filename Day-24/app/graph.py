"""
Linkific Enterprise AI Service - LangGraph Multi-Agent Workflow Engine
Constructs and compiles the StateGraph workflow with conditional routing and error handling.
"""

import time
import uuid
from typing import Dict, Any, Optional

try:
    from langgraph.graph import StateGraph, START, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    START = "__start__"
    END = "__end__"

    class StateGraph:
        """Pure-Python fallback graph runtime for environments without langgraph."""
        def __init__(self, state_schema):
            self.state_schema = state_schema
            self.nodes = {}
            self.edges = []
            self.conditional_edges = []

        def add_node(self, name, func):
            self.nodes[name] = func

        def add_edge(self, source, target):
            self.edges.append((source, target))

        def add_conditional_edges(self, source, router, path_map=None):
            self.conditional_edges.append((source, router, path_map))

        def compile(self):
            return FallbackCompiledGraph(self)

    class FallbackCompiledGraph:
        def __init__(self, graph: StateGraph):
            self.graph = graph

        def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
            current_state = dict(state)
            current_node = "coordinator_plan"

            while current_node and current_node != END:
                node_func = self.graph.nodes.get(current_node)
                if not node_func:
                    break
                updates = node_func(current_state)
                # Apply updates
                for k, v in updates.items():
                    if k == "communication_log" and k in current_state:
                        current_state[k] = current_state[k] + v
                    elif k == "errors" and k in current_state:
                        current_state[k] = current_state[k] + v
                    elif k == "milestones" and k in current_state:
                        from app.state import update_milestones
                        current_state[k] = update_milestones(current_state[k], v)
                    elif k == "critic_reviews" and k in current_state:
                        current_state[k] = current_state[k] + v
                    else:
                        current_state[k] = v

                # Route
                routed = False
                for src, router, p_map in self.graph.conditional_edges:
                    if src == current_node:
                        dest = router(current_state)
                        current_node = p_map.get(dest, dest) if p_map else dest
                        routed = True
                        break
                if not routed:
                    for src, dst in self.graph.edges:
                        if src == current_node:
                            current_node = dst
                            routed = True
                            break
                if not routed:
                    break
            return current_state


from app.state import MultiAgentState, create_initial_state
from app.schemas import WorkflowResponse, WorkflowStatus
from app.nodes import (
    coordinator_plan,
    coordinator_synthesize,
    research_node,
    analyzer_node,
    critic_node,
    writer_node,
    error_handler_node
)
from app.core.config import get_settings
from app.core.logging_config import get_logger, set_correlation_id
from app.core.metrics import metrics_registry

logger = get_logger("LinkificService.Graph")


# ==============================================================================
# Conditional Edge Routers
# ==============================================================================
def route_after_plan(state: MultiAgentState) -> str:
    """Routes after coordinator plan: directly to error_handler if invalid query."""
    if state.get("errors"):
        return "error_handler"
    return "researcher"


def route_after_research(state: MultiAgentState) -> str:
    """Routes after research: streamlined goes to writer, comprehensive goes to analyzer."""
    if state.get("errors"):
        return "error_handler"
    mode = state.get("mode", "streamlined")
    if mode == "streamlined":
        return "writer"
    return "analyzer"


def route_after_analyzer(state: MultiAgentState) -> str:
    """Routes after analyzer: to critic or error_handler."""
    if state.get("errors"):
        return "error_handler"
    return "critic"


def route_after_critic(state: MultiAgentState) -> str:
    """
    Evaluates Critic verdict:
    If approved -> routes to Writer
    If rejected & revisions remaining -> routes back to Analyzer
    """
    reviews = state.get("critic_reviews", [])
    if reviews and reviews[-1].verdict == "rejected":
        return "analyzer"
    return "writer"


# ==============================================================================
# Graph Builder
# ==============================================================================
def build_multi_agent_graph():
    """
    Constructs and compiles the official LangGraph Multi-Agent StateGraph.
    """
    workflow = StateGraph(MultiAgentState)

    # 1. Register Nodes
    workflow.add_node("coordinator_plan", coordinator_plan)
    workflow.add_node("researcher", research_node)
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("coordinator_synthesize", coordinator_synthesize)
    workflow.add_node("error_handler", error_handler_node)

    # 2. Add Ingress Edge
    workflow.add_edge(START, "coordinator_plan")

    # 3. Add Conditional Routing Edges
    workflow.add_conditional_edges(
        "coordinator_plan",
        route_after_plan,
        {
            "researcher": "researcher",
            "error_handler": "error_handler"
        }
    )

    workflow.add_conditional_edges(
        "researcher",
        route_after_research,
        {
            "writer": "writer",
            "analyzer": "analyzer",
            "error_handler": "error_handler"
        }
    )

    workflow.add_conditional_edges(
        "analyzer",
        route_after_analyzer,
        {
            "critic": "critic",
            "error_handler": "error_handler"
        }
    )

    workflow.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "writer": "writer",
            "analyzer": "analyzer"
        }
    )

    workflow.add_edge("writer", "coordinator_synthesize")
    workflow.add_edge("coordinator_synthesize", END)
    workflow.add_edge("error_handler", END)

    # 4. Compile Graph
    compiled = workflow.compile()
    logger.info(f"Compiled MultiAgentStateGraph successfully (LangGraph Available: {LANGGRAPH_AVAILABLE})")
    return compiled


# Module-level compiled graph cache
_COMPILED_GRAPH = None


def get_compiled_graph():
    """Singleton getter for the compiled graph."""
    global _COMPILED_GRAPH
    if _COMPILED_GRAPH is None:
        _COMPILED_GRAPH = build_multi_agent_graph()
    return _COMPILED_GRAPH


# ==============================================================================
# Workflow Invocation Service
# ==============================================================================
def execute_multi_agent_workflow(
    query: str,
    mode: str = "streamlined",
    correlation_id: Optional[str] = None
) -> WorkflowResponse:
    """
    Executes the multi-agent workflow end-to-end, recording operational telemetry.
    """
    start_time = time.time()
    w_id = correlation_id or f"WF-{uuid.uuid4().hex[:8].upper()}"
    set_correlation_id(w_id)

    metrics_registry.increment_active_workflows()
    logger.info(f"Starting multi-agent workflow '{w_id}' | Mode: {mode} | Query: '{query}'")

    settings = get_settings()
    initial_state = create_initial_state(
        query=query,
        mode=mode,
        max_revisions=settings.MAX_WORKFLOW_REVISIONS,
        workflow_id=w_id
    )

    try:
        graph = get_compiled_graph()
        final_state = graph.invoke(initial_state)

        duration = round(time.time() - start_time, 4)
        status = final_state.get("status", WorkflowStatus.COMPLETED)
        if isinstance(status, WorkflowStatus):
            status_val = status.value
        else:
            status_val = str(status)

        metrics_registry.record_workflow_execution(mode=mode, status=status_val, duration_seconds=duration)

        critic_reviews = final_state.get("critic_reviews", [])
        critic_approved = True
        if critic_reviews:
            critic_approved = (critic_reviews[-1].verdict == "approved")

        comm_log = final_state.get("communication_log", [])
        milestones = final_state.get("milestones", [])
        report = final_state.get("final_report")
        answer = final_state.get("final_answer", "Workflow completed.")
        errors = final_state.get("errors", [])

        response = WorkflowResponse(
            workflow_id=w_id,
            correlation_id=w_id,
            status=status_val,
            execution_time_seconds=duration,
            final_answer=answer,
            critic_approved=critic_approved,
            milestones_completed=len([m for m in milestones if m.status == "completed"]),
            report=report,
            communication_hops=len(comm_log),
            errors=errors
        )
        logger.info(f"Workflow '{w_id}' finished in {duration}s with status '{status_val}'")
        return response

    except Exception as e:
        duration = round(time.time() - start_time, 4)
        logger.exception(f"Unhandled exception during workflow '{w_id}': {str(e)}")
        metrics_registry.record_workflow_execution(mode=mode, status="failed", duration_seconds=duration)
        return WorkflowResponse(
            workflow_id=w_id,
            correlation_id=w_id,
            status="failed",
            execution_time_seconds=duration,
            final_answer=f"Execution error: {str(e)}",
            critic_approved=False,
            milestones_completed=0,
            report=None,
            communication_hops=0,
            errors=[str(e)]
        )
    finally:
        metrics_registry.decrement_active_workflows()
