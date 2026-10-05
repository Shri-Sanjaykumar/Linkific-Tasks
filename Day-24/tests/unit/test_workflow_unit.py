"""
Unit Tests: Multi-Agent Nodes & StateGraph Execution
Validates each individual agent reasoning node and end-to-end workflow execution.
"""

from app.state import create_initial_state, MultiAgentState
from app.schemas import AgentRole, WorkflowStatus, MessageType
from app.nodes import (
    coordinator_plan,
    coordinator_synthesize,
    research_node,
    analyzer_node,
    critic_node,
    writer_node,
    error_handler_node
)
from app.graph import build_multi_agent_graph, execute_multi_agent_workflow


def test_coordinator_plan_unit():
    """Verify coordinator planning node generates milestones and task assignment message."""
    state = create_initial_state("What are the remote work policies?", mode="streamlined")
    result = coordinator_plan(state)

    assert result["status"] == WorkflowStatus.PLANNING
    assert result["next_step"] == "researcher"
    assert len(result["milestones"]) == 4
    assert len(result["communication_log"]) == 1
    assert result["communication_log"][0].message_type == MessageType.TASK_ASSIGNMENT


def test_coordinator_plan_empty_query_fails():
    """Verify coordinator flags short/empty queries and routes to error handler."""
    state = create_initial_state("  ", mode="streamlined")
    result = coordinator_plan(state)

    assert result["status"] == WorkflowStatus.FAILED
    assert result["next_step"] == "error_handler"
    assert len(result["errors"]) > 0


def test_researcher_node_unit():
    """Verify researcher retrieves grounded evidence items and sources."""
    state = create_initial_state("What are the policies on paid leave and hardware allowance?", mode="streamlined")
    plan_res = coordinator_plan(state)
    state["milestones"] = plan_res["milestones"]

    res = research_node(state)
    assert res["status"] == WorkflowStatus.RESEARCHING
    assert res["research_findings"] is not None
    assert len(res["research_findings"].items) > 0
    assert "DOC-POL-001" in res["research_findings"].sources_used or "DOC-POL-002" in res["research_findings"].sources_used


def test_analyzer_node_unit():
    """Verify analyzer creates cognitive insight clusters."""
    state = create_initial_state("What are the CI/CD and incident response protocols?", mode="comprehensive")
    plan_res = coordinator_plan(state)
    state["milestones"] = plan_res["milestones"]
    res_findings = research_node(state)
    state["research_findings"] = res_findings["research_findings"]

    ana_res = analyzer_node(state)
    assert ana_res["status"] == WorkflowStatus.ANALYZING
    assert ana_res["analysis_result"] is not None
    assert len(ana_res["analysis_result"].insights) > 0


def test_critic_node_approved():
    """Verify critic approves valid grounded research findings."""
    state = create_initial_state("What are corporate leave policies?", mode="comprehensive")
    res_findings = research_node(state)
    state["research_findings"] = res_findings["research_findings"]
    ana_res = analyzer_node(state)
    state["analysis_result"] = ana_res["analysis_result"]

    critic_res = critic_node(state)
    assert critic_res["status"] == WorkflowStatus.REVIEWING
    assert critic_res["next_step"] == "writer"
    assert critic_res["critic_reviews"][0].verdict == "approved"


def test_critic_node_circuit_breaker():
    """Verify critic circuit breaker triggers approval when max revisions are reached."""
    state = create_initial_state("Query with empty evidence", mode="comprehensive")
    state["research_findings"] = None  # Force failure
    state["revision_count"] = 2
    state["max_revisions"] = 2

    critic_res = critic_node(state)
    assert critic_res["next_step"] == "writer"
    assert critic_res["critic_reviews"][0].verdict == "approved"


def test_writer_node_unit():
    """Verify writer synthesizes executive brief with grounded citations."""
    state = create_initial_state("What are the policies on paid leave and hardware?", mode="streamlined")
    res_findings = research_node(state)
    state["research_findings"] = res_findings["research_findings"]

    writer_res = writer_node(state)
    assert writer_res["status"] == WorkflowStatus.WRITING
    assert writer_res["final_report"] is not None
    assert len(writer_res["final_report"].citations) > 0


def test_coordinator_synthesize_unit():
    """Verify final synthesis produces user answer and completes workflow."""
    state = create_initial_state("What are the policies on paid leave?", mode="streamlined")
    res_findings = research_node(state)
    state["research_findings"] = res_findings["research_findings"]
    w_res = writer_node(state)
    state["final_report"] = w_res["final_report"]

    synth_res = coordinator_synthesize(state)
    assert synth_res["status"] == WorkflowStatus.COMPLETED
    assert synth_res["final_answer"] is not None
    assert len(synth_res["final_answer"]) > 20


def test_error_handler_node_unit():
    """Verify error handler terminates failed state gracefully."""
    state = create_initial_state("Invalid query", mode="streamlined")
    state["errors"] = ["Corpus database offline."]

    err_res = error_handler_node(state)
    assert err_res["status"] == WorkflowStatus.FAILED
    assert "Corpus database offline" in err_res["final_answer"]


def test_end_to_end_streamlined_execution():
    """Verify full end-to-end streamlined workflow execution preserves factual constants."""
    response = execute_multi_agent_workflow(
        query="What are the corporate guidelines regarding remote work, hardware allowances, and core collaboration hours?",
        mode="streamlined"
    )

    assert response.status == "completed"
    assert response.critic_approved is True
    assert response.milestones_completed >= 3
    assert response.communication_hops >= 4
    # Verify factual preservation
    assert "1.5" in response.final_answer or "leave" in response.final_answer.lower()


def test_end_to_end_comprehensive_execution():
    """Verify full end-to-end comprehensive workflow execution (6 milestones)."""
    response = execute_multi_agent_workflow(
        query="What are the protocols for Severity 1 production incident escalation, CI/CD code review SLAs, and test coverage gates?",
        mode="comprehensive"
    )

    assert response.status == "completed"
    assert response.critic_approved is True
    assert response.milestones_completed >= 5
    assert response.communication_hops >= 6
