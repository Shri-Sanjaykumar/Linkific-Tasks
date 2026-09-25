"""Tests for LangGraph error handling, fault tolerance, and circuit breakers."""

import pytest
from app.graph import build_multi_agent_graph, _route_after_research, _route_after_critic
from app.state import create_initial_state
from app.schemas import MessageType, WorkflowStatus, AgentRole, InsightItem, AnalysisResult
from app.nodes.researcher import search_policy_documents
from app.nodes.critic import critic_node


def test_empty_query_error_handling():
    graph = build_multi_agent_graph()
    initial_state = create_initial_state(
        query="   ",
        workflow_id="WF-ERR-EMPTY",
        mode="streamlined",
    )
    final_state = graph.invoke(initial_state)

    assert final_state["status"] == WorkflowStatus.FAILED
    assert len(final_state["errors"]) > 0
    assert any("too short" in err for err in final_state["errors"])

    # Error message logged in communication_log
    error_msgs = [m for m in final_state["communication_log"] if m.message_type == MessageType.ERROR_NOTIFICATION]
    assert len(error_msgs) >= 1


def test_missing_corpus_file_fallback():
    # Calling search_policy_documents with a non-existent file
    findings = search_policy_documents("leave policy", corpus_path="non_existent_corpus_file.json")
    assert findings.relevant_documents_count >= 1
    # Fallback corpus should still yield default documents
    assert len(findings.evidence_items) > 0


def test_route_after_research_error_routing():
    state = create_initial_state(query="test", workflow_id="WF-ROUTE-ERR")
    state["errors"] = ["An unhandled error occurred in researcher"]
    next_node = _route_after_research(state)
    assert next_node == "error_handler"


def test_route_after_critic_circuit_breaker():
    state = create_initial_state(query="test", workflow_id="WF-CRITIC-CB", mode="comprehensive")
    # Case 1: next_step is analyzer -> routes to analyzer
    state["next_step"] = "analyzer"
    assert _route_after_critic(state) == "analyzer"

    # Case 2: next_step is writer -> routes to writer
    state["next_step"] = "writer"
    assert _route_after_critic(state) == "writer"

    # Case 3: Verify critic_node triggers circuit breaker at max_revisions
    # Create an analysis result with an ungrounded claim to trigger defect
    state["analysis_result"] = AnalysisResult(
        key_insights=[
            InsightItem(
                topic="Test",
                statement="Invalid statement with no citations and dangling to",
                supporting_evidence_ids=[],
                confidence=0.5,
                is_assumption=False,
            )
        ]
    )
    # When revision_count = 0 < max_revisions=2
    state["revision_count"] = 0
    state["max_revisions"] = 2
    update = critic_node(state)
    assert update["next_step"] == "analyzer"
    assert update["revision_count"] == 1

    # When revision_count = 2 == max_revisions
    state["revision_count"] = 2
    update_cb = critic_node(state)
    assert update_cb["next_step"] == "writer"
