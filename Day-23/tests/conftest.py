"""Shared fixtures and configuration for Day 23 multi-agent test suite."""

import sys
from pathlib import Path
import pytest

# Ensure Day-23 directory is in Python path
DAY_23_DIR = Path(__file__).resolve().parent.parent
if str(DAY_23_DIR) not in sys.path:
    sys.path.insert(0, str(DAY_23_DIR))

from app.schemas import (
    AgentRole,
    MessageType,
    WorkflowStatus,
    AgentMessage,
    EvidenceItem,
    ResearchFindings,
    InsightItem,
    AnalysisResult,
    CriticReview,
    WriterReport,
    Milestone,
    WorkflowRequest,
    WorkflowResponse,
)
from app.state import create_initial_state, MultiAgentState


@pytest.fixture
def sample_query() -> str:
    return "What are the corporate guidelines regarding remote work, hardware allowances, and core collaboration hours?"


@pytest.fixture
def sample_initial_state(sample_query) -> MultiAgentState:
    return create_initial_state(
        query=sample_query,
        workflow_id="TEST-WF-001",
        mode="streamlined",
        max_revisions=2,
    )


@pytest.fixture
def sample_evidence() -> EvidenceItem:
    return EvidenceItem(
        source_id="DOC-POL-001",
        title="Corporate Leave, Attendance, and Remote Work Policy",
        category="hr_policy",
        excerpt="All Linkific employees and interns are entitled to 1.5 paid leave days per completed calendar month.",
        relevance_score=0.95,
        version="2.4",
        author="People Operations"
    )


@pytest.fixture
def sample_research_findings(sample_evidence) -> ResearchFindings:
    return ResearchFindings(
        query="What are the leave rules?",
        evidence=[sample_evidence],
        unresolved_queries=[],
        search_parameters={"top_k": 5},
        status="complete"
    )


@pytest.fixture
def sample_agent_message() -> AgentMessage:
    return AgentMessage(
        message_id="MSG-TEST-001",
        correlation_id="WF-TEST-001",
        sender=AgentRole.COORDINATOR,
        recipient=AgentRole.RESEARCHER,
        message_type=MessageType.TASK_ASSIGNMENT,
        payload={"query": "test query", "mode": "streamlined"},
        summary="Coordinator assigned research task to Research Agent",
    )
