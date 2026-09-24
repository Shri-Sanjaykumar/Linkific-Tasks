"""
Day 22 — Schema Contract & Model Validation Tests
Validates all Pydantic v2 data models, boundary constraints, and serialization.
"""

import pytest
from pydantic import ValidationError
from app.schemas import (
    AgentRole,
    MessageType,
    MessageStatus,
    WorkflowStatus,
    CriticVerdict,
    DefectSeverity,
    DefectCategory,
    EvidenceItem,
    ResearchFindings,
    InsightItem,
    AnalysisResult,
    DefectItem,
    CriticReview,
    ReportSection,
    WriterReport,
    ExecutionMilestone,
    ExecutionPlan,
    AgentMessage,
    WorkflowRequest,
    WorkflowResponse
)


def test_evidence_item_valid():
    """Verify valid EvidenceItem instantiates correctly."""
    item = EvidenceItem(
        source_id="DOC-POL-001",
        title="Leave Policy",
        category="HR",
        excerpt="1.5 days per month",
        relevance_score=0.85
    )
    assert item.source_id == "DOC-POL-001"
    assert item.relevance_score == 0.85
    assert item.version == "1.0"


def test_evidence_item_score_boundary_rejected():
    """Verify relevance_score must be between 0.0 and 1.0."""
    with pytest.raises(ValidationError):
        EvidenceItem(
            source_id="DOC-POL-001",
            title="Leave Policy",
            category="HR",
            excerpt="1.5 days",
            relevance_score=1.5  # Invalid > 1.0
        )

    with pytest.raises(ValidationError):
        EvidenceItem(
            source_id="DOC-POL-001",
            title="Leave Policy",
            category="HR",
            excerpt="1.5 days",
            relevance_score=-0.1  # Invalid < 0.0
        )


def test_insight_item_confidence_bounds():
    """Verify InsightItem confidence constraints."""
    insight = InsightItem(
        topic="Security",
        statement="MFA is mandatory across all repositories.",
        supporting_evidence_ids=["DOC-POL-002"],
        confidence=0.95
    )
    assert insight.confidence == 0.95
    assert not insight.is_assumption

    with pytest.raises(ValidationError):
        InsightItem(
            topic="Security",
            statement="MFA is mandatory.",
            confidence=1.2  # Out of bounds
        )


def test_critic_defect_and_review_schema():
    """Verify CriticReview and DefectItem models."""
    defect = DefectItem(
        category=DefectCategory.UNSUPPORTED_CLAIM,
        severity=DefectSeverity.MAJOR,
        description="Missing citation for remote allowance claim.",
        target_agent=AgentRole.ANALYZER,
        actionable_correction="Attach DOC-POL-002 reference."
    )
    assert defect.target_agent == AgentRole.ANALYZER

    review = CriticReview(
        verdict=CriticVerdict.REVISION_REQUIRED,
        quality_score=0.65,
        defects=[defect],
        citation_coverage_pct=50.0,
        unsupported_claims_count=1,
        feedback_summary="Defects detected requiring correction."
    )
    assert review.verdict == CriticVerdict.REVISION_REQUIRED
    assert len(review.defects) == 1
    assert review.quality_score == 0.65


def test_writer_report_schema():
    """Verify WriterReport structure and sections."""
    section = ReportSection(
        title="Human Resources",
        content="Core collaboration hours are 10 AM to 5 PM.",
        cited_sources=["DOC-POL-001"]
    )
    report = WriterReport(
        title="Enterprise Brief",
        executive_summary="Summary of findings.",
        sections=[section],
        evidence_traceability_matrix={"INS-001": ["DOC-POL-001"]},
        limitations=["Scope limited to current corpus."],
        recommendations=["Align with department heads."],
        markdown_output="# Enterprise Brief\nSummary..."
    )
    assert report.title == "Enterprise Brief"
    assert len(report.sections) == 1
    assert "INS-001" in report.evidence_traceability_matrix


def test_agent_message_envelope_validation():
    """Verify AgentMessage creation and status defaults."""
    msg = AgentMessage(
        workflow_id="WF-12345",
        task_id="TASK-RES-001",
        sender=AgentRole.COORDINATOR,
        receiver=AgentRole.RESEARCH,
        message_type=MessageType.TASK_ASSIGNMENT,
        payload={"query": "remote work"}
    )
    assert msg.status == MessageStatus.SENT
    assert msg.sender == AgentRole.COORDINATOR
    assert msg.receiver == AgentRole.RESEARCH
    assert msg.workflow_id == "WF-12345"


def test_workflow_request_validation():
    """Verify WorkflowRequest rejects empty or whitespace-only queries."""
    req = WorkflowRequest(user_query="What is the remote work policy?")
    assert req.user_query == "What is the remote work policy?"

    with pytest.raises(ValidationError):
        WorkflowRequest(user_query="   ")

    with pytest.raises(ValidationError):
        WorkflowRequest(user_query="ab")  # Too short (< 3)
