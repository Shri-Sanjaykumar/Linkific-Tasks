"""Unit tests for individual LangGraph nodes."""

import pytest
from app.state import create_initial_state
from app.schemas import AgentRole, MessageType, WorkflowStatus
from app.nodes.coordinator import coordinator_plan_node, coordinator_synthesize_node
from app.nodes.researcher import researcher_node
from app.nodes.analyzer import analyzer_node
from app.nodes.critic import critic_node
from app.nodes.writer import writer_node
from app.nodes.error_handler import error_handler_node


def test_coordinator_plan_node(sample_query):
    state = create_initial_state(query=sample_query, workflow_id="WF-TEST-001", mode="streamlined")
    update = coordinator_plan_node(state)

    assert update["status"] == WorkflowStatus.PLANNING
    assert len(update["milestones"]) == 4
    assert len(update["communication_log"]) == 1
    assert update["communication_log"][0].message_type == MessageType.TASK_ASSIGNMENT


def test_coordinator_plan_node_empty_query():
    state = create_initial_state(query="   ", workflow_id="WF-TEST-EMPTY")
    update = coordinator_plan_node(state)

    assert "errors" in update
    assert len(update["errors"]) > 0
    assert "too short" in update["errors"][0]


def test_researcher_node(sample_query):
    state = create_initial_state(query=sample_query, workflow_id="WF-TEST-002", mode="streamlined")
    update = researcher_node(state)

    assert update["current_agent"] == AgentRole.RESEARCHER
    assert update["research_findings"] is not None
    assert update["research_findings"].relevant_documents_count >= 1

    # Check factual preservation in excerpts
    all_excerpts = " ".join([e.excerpt for e in update["research_findings"].evidence_items])
    assert "1.5" in all_excerpts or "$500" in all_excerpts or "10:00 AM" in all_excerpts

    assert len(update["communication_log"]) == 1
    assert update["communication_log"][0].message_type == MessageType.RESEARCH_SUBMISSION


def test_analyzer_node(sample_initial_state):
    # Prepare state with research findings
    res_update = researcher_node(sample_initial_state)
    sample_initial_state["research_findings"] = res_update["research_findings"]

    update = analyzer_node(sample_initial_state)
    assert update["current_agent"] == AgentRole.ANALYZER
    assert update["analysis_result"] is not None
    assert len(update["analysis_result"].insights) > 0
    assert len(update["communication_log"]) == 1
    assert update["communication_log"][0].message_type == MessageType.ANALYSIS_SUBMISSION


def test_critic_node_approved(sample_initial_state):
    res_update = researcher_node(sample_initial_state)
    sample_initial_state["research_findings"] = res_update["research_findings"]
    ana_update = analyzer_node(sample_initial_state)
    sample_initial_state["analysis_result"] = ana_update["analysis_result"]

    update = critic_node(sample_initial_state)
    assert update["current_agent"] == AgentRole.CRITIC
    assert len(update["critic_reviews"]) == 1
    review = update["critic_reviews"][0]
    assert review.score >= 0.80
    assert review.is_approved is True
    assert len(update["communication_log"]) == 1
    assert update["communication_log"][0].message_type == MessageType.CRITIC_REVIEW


def test_writer_node(sample_initial_state):
    res_update = researcher_node(sample_initial_state)
    sample_initial_state["research_findings"] = res_update["research_findings"]

    update = writer_node(sample_initial_state)
    assert update["current_agent"] == AgentRole.WRITER
    assert update["final_report"] is not None
    assert len(update["final_report"].sections) > 0
    assert len(update["final_report"].evidence_traceability_matrix) > 0
    assert len(update["communication_log"]) == 1
    assert update["communication_log"][0].message_type == MessageType.REPORT_DRAFT


def test_coordinator_synthesize_node(sample_initial_state):
    res_update = researcher_node(sample_initial_state)
    sample_initial_state["research_findings"] = res_update["research_findings"]
    wri_update = writer_node(sample_initial_state)
    sample_initial_state["final_report"] = wri_update["final_report"]

    update = coordinator_synthesize_node(sample_initial_state)
    assert update["status"] == WorkflowStatus.COMPLETED
    assert update["final_answer"] is not None
    assert len(update["final_answer"]) > 20
    assert len(update["communication_log"]) == 1
    assert update["communication_log"][0].message_type == MessageType.FINAL_ANSWER


def test_error_handler_node(sample_initial_state):
    sample_initial_state["errors"] = ["Critical failure test"]
    update = error_handler_node(sample_initial_state)

    assert update["status"] == WorkflowStatus.FAILED
    assert update["current_agent"] == AgentRole.ERROR_HANDLER
    assert "error" in update["final_answer"].lower() or "unable" in update["final_answer"].lower()
    assert len(update["communication_log"]) == 1
    assert update["communication_log"][0].message_type == MessageType.ERROR_NOTIFICATION
