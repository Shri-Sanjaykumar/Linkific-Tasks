"""Unit tests for Day 23 LangGraph State and Reducers."""

import operator
from datetime import datetime, timezone
from app.state import create_initial_state, update_milestones, MultiAgentState
from app.schemas import Milestone, AgentRole, AgentMessage, MessageType, CriticReview, CriticVerdict, WorkflowStatus


def test_create_initial_state():
    state = create_initial_state(
        query="What is the leave policy?",
        workflow_id="WF-INIT-001",
        mode="streamlined",
        max_revisions=3,
    )
    assert state["workflow_id"] == "WF-INIT-001"
    assert state["query"] == "What is the leave policy?"
    assert state["mode"] == "streamlined"
    assert state["status"] == WorkflowStatus.INITIALIZED
    assert state["current_agent"] == AgentRole.USER
    assert state["revision_count"] == 0
    assert state["max_revisions"] == 3
    assert len(state["communication_log"]) == 1
    assert state["communication_log"][0].message_type == MessageType.USER_REQUEST
    assert state["critic_reviews"] == []
    assert state["errors"] == []
    assert len(state["milestones"]) == 0


def test_update_milestones_reducer():
    initial_milestones = [
        Milestone(step_number=1, name="Planning", assigned_agent=AgentRole.COORDINATOR, description="Plan tasks", status="pending"),
        Milestone(step_number=2, name="Research", assigned_agent=AgentRole.RESEARCHER, description="Gather evidence", status="pending"),
    ]

    now_iso = datetime.now(timezone.utc).isoformat()
    updates = [
        Milestone(step_number=1, name="Planning", assigned_agent=AgentRole.COORDINATOR, description="Plan tasks", status="completed", completed_at=now_iso),
        Milestone(step_number=3, name="Writing", assigned_agent=AgentRole.WRITER, description="Draft report", status="in_progress"),
    ]

    result = update_milestones(initial_milestones, updates)

    assert len(result) == 3
    # Step 1 should be updated to completed
    assert result[0].step_number == 1
    assert result[0].status == "completed"
    assert result[0].completed_at == now_iso

    # Step 2 should be preserved as pending
    assert result[1].step_number == 2
    assert result[1].status == "pending"

    # Step 3 should be newly appended
    assert result[2].step_number == 3
    assert result[2].status == "in_progress"


def test_communication_log_append_reducer():
    log1 = [
        AgentMessage(
            message_id="MSG-01",
            correlation_id="WF-01",
            sender=AgentRole.USER,
            recipient=AgentRole.COORDINATOR,
            message_type=MessageType.USER_REQUEST,
            payload={},
            summary="User inquiry",
        )
    ]
    log2 = [
        AgentMessage(
            message_id="MSG-02",
            correlation_id="WF-01",
            sender=AgentRole.COORDINATOR,
            recipient=AgentRole.RESEARCHER,
            message_type=MessageType.TASK_ASSIGNMENT,
            payload={},
            summary="Coordinator dispatch",
        )
    ]

    combined = operator.add(log1, log2)
    assert len(combined) == 2
    assert combined[0].message_id == "MSG-01"
    assert combined[1].message_id == "MSG-02"


def test_critic_reviews_reducer():
    rev1 = [
        CriticReview(
            review_id="REV-1",
            verdict=CriticVerdict.REVISION_REQUIRED,
            quality_score=0.70,
            citation_coverage_pct=70.0,
            revision_notes="Needs more citation rigor.",
        )
    ]
    rev2 = [
        CriticReview(
            review_id="REV-2",
            verdict=CriticVerdict.APPROVED,
            quality_score=0.92,
            citation_coverage_pct=100.0,
            revision_notes="All clauses verified.",
        )
    ]

    combined = operator.add(rev1, rev2)
    assert len(combined) == 2
    assert combined[0].is_approved is False
    assert combined[1].is_approved is True
