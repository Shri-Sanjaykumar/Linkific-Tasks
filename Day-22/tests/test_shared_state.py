"""
Day 22 — Shared State Manager & Concurrency Tests
Validates:
- Centralized state initialization
- Role-based field ownership & permission boundaries (StatePermissionError)
- Snapshot immutability & isolation
- State transition audit history recording
- Multi-threaded mutation safety
"""

import threading
import pytest
from app.state import SharedStateManager, StatePermissionError
from app.schemas import (
    AgentRole,
    WorkflowStatus,
    ExecutionPlan,
    ResearchFindings,
    EvidenceItem,
    AnalysisResult,
    InsightItem,
    CriticReview,
    CriticVerdict,
    WriterReport
)


def test_shared_state_initialization(state_manager):
    """Verify SharedStateManager initializes with proper defaults."""
    assert state_manager.workflow_id == "TEST-WF-001"
    assert state_manager.current_status == WorkflowStatus.INITIALIZED
    assert state_manager.revision_count == 0

    snapshot = state_manager.get_snapshot()
    assert snapshot.user_query == "What is the corporate leave and remote hardware policy?"
    assert len(snapshot.transition_history) == 0


def test_snapshot_isolation(state_manager):
    """Verify modifying a returned snapshot does not mutate the authoritative manager state."""
    snapshot = state_manager.get_snapshot()
    snapshot.errors.append("Fake external error")

    fresh_snapshot = state_manager.get_snapshot()
    assert len(fresh_snapshot.errors) == 0


def test_field_ownership_coordinator_permissions(state_manager):
    """Verify only Coordinator can modify workflow status and plan."""
    # Legitimate coordinator action
    state_manager.update_workflow_status(AgentRole.COORDINATOR, WorkflowStatus.PLANNING, "Starting")
    assert state_manager.current_status == WorkflowStatus.PLANNING

    # Unauthorized action by Research Agent
    with pytest.raises(StatePermissionError) as exc_info:
        state_manager.update_workflow_status(AgentRole.RESEARCH, WorkflowStatus.COMPLETED, "Unauthorized")
    assert "not authorized to modify workflow status" in str(exc_info.value)


def test_field_ownership_research_agent_permissions(state_manager, sample_evidence):
    """Verify only Research Agent can set research findings."""
    findings = ResearchFindings(query="test", evidence=sample_evidence)

    # Unauthorized attempt by Analyzer
    with pytest.raises(StatePermissionError):
        state_manager.set_research_findings(AgentRole.ANALYZER, findings)

    # Authorized attempt by Research Agent
    state_manager.set_research_findings(AgentRole.RESEARCH, findings)
    snapshot = state_manager.get_snapshot()
    assert snapshot.research_findings is not None
    assert len(snapshot.research_findings.evidence) == 2


def test_field_ownership_analyzer_permissions(state_manager, sample_analysis):
    """Verify only Analyzer Agent can set analysis results."""
    # Unauthorized attempt by Critic
    with pytest.raises(StatePermissionError):
        state_manager.set_analysis_result(AgentRole.CRITIC, sample_analysis)

    # Authorized attempt by Analyzer
    state_manager.set_analysis_result(AgentRole.ANALYZER, sample_analysis)
    snapshot = state_manager.get_snapshot()
    assert snapshot.analysis_result is not None
    assert len(snapshot.analysis_result.key_insights) == 2


def test_field_ownership_critic_permissions(state_manager):
    """Verify only Critic Agent can add critic reviews."""
    review = CriticReview(
        verdict=CriticVerdict.APPROVED,
        quality_score=0.95,
        defects=[],
        citation_coverage_pct=100.0,
        unsupported_claims_count=0,
        feedback_summary="Excellent analysis"
    )

    # Unauthorized attempt by Writer
    with pytest.raises(StatePermissionError):
        state_manager.add_critic_review(AgentRole.WRITER, review)

    # Authorized attempt by Critic
    state_manager.add_critic_review(AgentRole.CRITIC, review)
    snapshot = state_manager.get_snapshot()
    assert len(snapshot.critic_reviews) == 1
    assert snapshot.critic_approved is True


def test_field_ownership_writer_permissions(state_manager):
    """Verify only Writer Agent can write final reports."""
    report = WriterReport(
        title="Test Report",
        executive_summary="Summary",
        sections=[],
        evidence_traceability_matrix={},
        limitations=[],
        recommendations=[]
    )

    # Unauthorized attempt by Coordinator
    with pytest.raises(StatePermissionError):
        state_manager.set_final_report(AgentRole.COORDINATOR, report)

    # Authorized attempt by Writer
    state_manager.set_final_report(AgentRole.WRITER, report)
    snapshot = state_manager.get_snapshot()
    assert snapshot.final_report is not None
    assert snapshot.final_report.title == "Test Report"


def test_transition_history_audit(state_manager, sample_evidence):
    """Verify every state transition is recorded in transition_history."""
    state_manager.update_workflow_status(AgentRole.COORDINATOR, WorkflowStatus.PLANNING, "Plan start")
    findings = ResearchFindings(query="test", evidence=sample_evidence)
    state_manager.set_research_findings(AgentRole.RESEARCH, findings)

    snapshot = state_manager.get_snapshot()
    assert len(snapshot.transition_history) == 2
    assert snapshot.transition_history[0].actor == AgentRole.COORDINATOR
    assert snapshot.transition_history[0].field_modified == "current_status"
    assert snapshot.transition_history[1].actor == AgentRole.RESEARCH
    assert snapshot.transition_history[1].field_modified == "research_findings"


def test_thread_safety_concurrent_updates(state_manager):
    """Verify thread-safe handling under concurrent status and warning mutations."""
    def worker(agent_role, idx):
        state_manager.update_agent_status(AgentRole.COORDINATOR, agent_role, f"status_{idx}")
        state_manager.add_warning(agent_role, f"Warning from thread {idx}")

    threads = []
    roles = [AgentRole.RESEARCH, AgentRole.ANALYZER, AgentRole.CRITIC, AgentRole.WRITER]
    for i, r in enumerate(roles):
        t = threading.Thread(target=worker, args=(r, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    snapshot = state_manager.get_snapshot()
    assert len(snapshot.warnings) == 4
    for r in roles:
        assert snapshot.agent_statuses[r].startswith("status_")
