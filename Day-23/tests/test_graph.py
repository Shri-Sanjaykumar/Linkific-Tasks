"""Integration tests for end-to-end LangGraph execution."""

import pytest
from app.graph import build_multi_agent_graph
from app.state import create_initial_state
from app.schemas import MessageType, AgentRole, WorkflowStatus


def test_build_multi_agent_graph():
    graph = build_multi_agent_graph()
    assert graph is not None
    # LangGraph compiled graph has invoke method
    assert hasattr(graph, "invoke")


def test_streamlined_execution(sample_query):
    graph = build_multi_agent_graph()
    initial_state = create_initial_state(
        query=sample_query,
        workflow_id="WF-STREAM-TEST",
        mode="streamlined",
    )
    final_state = graph.invoke(initial_state)

    assert final_state["status"] == WorkflowStatus.COMPLETED
    assert final_state["final_answer"] is not None
    assert final_state["final_report"] is not None

    # Check that communication log has exactly 5 hops
    log = final_state["communication_log"]
    assert len(log) == 5

    expected_types = [
        MessageType.USER_REQUEST,
        MessageType.TASK_ASSIGNMENT,
        MessageType.RESEARCH_SUBMISSION,
        MessageType.REPORT_DRAFT,
        MessageType.FINAL_ANSWER,
    ]
    for i, exp_type in enumerate(expected_types):
        assert log[i].message_type == exp_type

    # Verify factual preservation in final answer
    assert "1.5" in final_state["final_answer"] or "DOC-POL-001" in final_state["final_answer"]


def test_comprehensive_execution(sample_query):
    graph = build_multi_agent_graph()
    initial_state = create_initial_state(
        query=sample_query,
        workflow_id="WF-COMP-TEST",
        mode="comprehensive",
    )
    final_state = graph.invoke(initial_state)

    assert final_state["status"] == WorkflowStatus.COMPLETED
    assert final_state["final_answer"] is not None
    assert final_state["final_report"] is not None
    assert final_state["analysis_result"] is not None
    assert len(final_state["critic_reviews"]) >= 1

    # Check hops in comprehensive mode (at least 7 hops)
    log = final_state["communication_log"]
    assert len(log) >= 7

    types = [msg.message_type for msg in log]
    assert MessageType.USER_REQUEST in types
    assert MessageType.TASK_ASSIGNMENT in types
    assert MessageType.RESEARCH_SUBMISSION in types
    assert MessageType.ANALYSIS_SUBMISSION in types
    assert MessageType.CRITIC_REVIEW in types
    assert MessageType.REPORT_DRAFT in types
    assert MessageType.FINAL_ANSWER in types


def test_invalid_query_routes_to_error_handler():
    graph = build_multi_agent_graph()
    initial_state = create_initial_state(
        query="x",  # Invalid query
        workflow_id="WF-ERR-TEST",
        mode="streamlined",
    )
    final_state = graph.invoke(initial_state)

    assert final_state["status"] == WorkflowStatus.FAILED
    assert len(final_state["errors"]) > 0
    assert final_state["current_agent"] == AgentRole.ERROR_HANDLER

    types = [msg.message_type for msg in final_state["communication_log"]]
    assert MessageType.ERROR_NOTIFICATION in types
