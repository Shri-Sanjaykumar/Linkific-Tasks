"""Unit tests for Day 23 Pydantic schemas."""

import pytest
from pydantic import ValidationError

from app.schemas import (
    AgentRole,
    MessageType,
    WorkflowStatus,
    CriticVerdict,
    AgentMessage,
    EvidenceItem,
    ResearchFindings,
    InsightItem,
    AnalysisResult,
    CriticReview,
    WriterReport,
    ReportSection,
    Milestone,
    WorkflowRequest,
    WorkflowResponse,
)


def test_agent_role_enum():
    assert AgentRole.COORDINATOR == "coordinator_agent"
    assert AgentRole.RESEARCHER == "research_agent"
    assert AgentRole.ANALYZER == "analyzer_agent"
    assert AgentRole.CRITIC == "critic_agent"
    assert AgentRole.WRITER == "writer_agent"
    assert AgentRole.USER == "user"


def test_message_type_enum():
    assert MessageType.USER_REQUEST == "user_request"
    assert MessageType.TASK_ASSIGNMENT == "task_assignment"
    assert MessageType.RESEARCH_SUBMISSION == "research_submission"
    assert MessageType.ANALYSIS_SUBMISSION == "analysis_submission"
    assert MessageType.CRITIC_REVIEW == "critic_review"
    assert MessageType.REVISION_REQUEST == "revision_request"
    assert MessageType.REPORT_DRAFT == "report_draft"
    assert MessageType.FINAL_ANSWER == "final_answer"
    assert MessageType.ERROR_NOTIFICATION == "error_notification"


def test_agent_message_creation():
    msg = AgentMessage(
        message_id="MSG-101",
        correlation_id="WF-101",
        sender=AgentRole.USER,
        recipient=AgentRole.COORDINATOR,
        message_type=MessageType.USER_REQUEST,
        payload={"query": "test query"},
        summary="User submitted research inquiry",
    )
    assert msg.message_id == "MSG-101"
    assert msg.sender == AgentRole.USER
    assert msg.payload["query"] == "test query"
    assert msg.timestamp is not None


def test_evidence_item_creation():
    evd = EvidenceItem(
        source_id="DOC-POL-001",
        title="Leave Policy",
        category="hr",
        excerpt="1.5 paid leave days per month.",
        relevance_score=0.92,
        version="2.4",
        author="People Operations",
    )
    assert evd.source_id == "DOC-POL-001"
    assert "1.5" in evd.excerpt


def test_research_findings_creation(sample_evidence):
    rf = ResearchFindings(
        query="Policy rules",
        evidence=[sample_evidence],
        unresolved_queries=[],
        search_parameters={"top_k": 5},
        status="complete",
    )
    assert rf.relevant_documents_count == 1
    assert len(rf.evidence_items) == 1
    assert rf.evidence_items[0].source_id == "DOC-POL-001"


def test_insight_item_and_analysis_result():
    insight = InsightItem(
        topic="Working Hours",
        statement="Core collaboration hours are 10:00 AM to 5:00 PM IST.",
        supporting_evidence_ids=["DOC-POL-004"],
        confidence=0.95,
        is_assumption=False,
    )
    analysis = AnalysisResult(
        key_insights=[insight],
        thematic_clusters={"Working Hours": ["INS-001"]},
        cross_document_correlations=["Aligned with IT security"],
        identified_gaps=[],
        assumptions=[],
        overall_confidence=0.95,
    )
    assert len(analysis.insights) == 1
    assert analysis.insights[0].topic == "Working Hours"


def test_critic_review_approval():
    review = CriticReview(
        review_id="REV-001",
        verdict=CriticVerdict.APPROVED,
        quality_score=0.92,
        citation_coverage_pct=100.0,
        defects=[],
        revision_notes="All facts verified with perfect citation mapping.",
    )
    assert review.is_approved is True
    assert review.score >= 0.80
    assert len(review.defects) == 0


def test_writer_report():
    report = WriterReport(
        report_id="REP-001",
        title="Corporate Policy Intelligence Brief",
        executive_summary="Summary of findings.",
        sections=[
            ReportSection(
                title="Leave Policy",
                content="1.5 days accrued per month.",
                cited_sources=["DOC-POL-001"],
            )
        ],
        evidence_traceability_matrix={"1.5 paid leave days": ["DOC-POL-001"]},
        limitations=[],
        recommendations=[],
        markdown_output="# Executive Report\nDetailed brief.",
    )
    assert report.report_id == "REP-001"
    assert "DOC-POL-001" in report.sections[0].cited_sources


def test_milestone_schema():
    m = Milestone(
        step_number=1,
        name="Research Retrieval",
        assigned_agent=AgentRole.RESEARCHER,
        description="Retrieve evidence",
        status="pending",
    )
    assert m.status == "pending"
    assert m.started_at is None
    assert m.completed_at is None


def test_workflow_request_validation():
    req = WorkflowRequest(query="Valid query for test", mode="streamlined")
    assert req.query == "Valid query for test"
    assert req.mode == "streamlined"

    with pytest.raises(ValidationError):
        WorkflowRequest(query="ab")  # min_length=3


def test_workflow_response_creation():
    resp = WorkflowResponse(
        workflow_id="WF-100",
        query="Test query",
        status=WorkflowStatus.COMPLETED,
        final_answer="Final consolidated answer.",
        critic_approved=True,
        milestones=[],
        communication_log=[],
        execution_time_seconds=0.02,
    )
    assert resp.status == WorkflowStatus.COMPLETED
