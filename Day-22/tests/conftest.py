"""
Day 22 — PyTest Test Configuration & Fixtures
Provides isolated state managers, message buses, temporary audit loggers,
and mocked enterprise corpus data for repeatable testing.
"""

import os
import sys
import tempfile
import pytest

# Ensure Day-22 root is on sys.path
DAY22_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if DAY22_ROOT not in sys.path:
    sys.path.insert(0, DAY22_ROOT)

from app.state import SharedStateManager
from app.communication import MessageBus
from app.schemas import AgentRole, WorkflowStatus, EvidenceItem, ResearchFindings, InsightItem, AnalysisResult
from app.config import config


@pytest.fixture
def temp_audit_file(tmp_path):
    """Provides a temporary audit log file path isolated per test."""
    log_file = tmp_path / "test_activity_audit.jsonl"
    return str(log_file)


@pytest.fixture
def state_manager():
    """Provides an isolated SharedStateManager initialized for a test query."""
    return SharedStateManager(
        workflow_id="TEST-WF-001",
        user_query="What is the corporate leave and remote hardware policy?",
        context={"test_env": True},
        max_revisions=2
    )


@pytest.fixture
def message_bus(state_manager, temp_audit_file):
    """Provides a MessageBus instance linked to the test state manager and temp audit file."""
    return MessageBus(state_manager=state_manager, audit_file_path=temp_audit_file)


@pytest.fixture
def sample_evidence():
    """Provides standardized sample EvidenceItem objects."""
    return [
        EvidenceItem(
            source_id="DOC-POL-001",
            title="Corporate Leave Policy",
            category="Human Resources",
            excerpt="Employees receive 1.5 paid leave days per month. Core hours are 10 AM to 5 PM IST.",
            relevance_score=0.92,
            version="2.4",
            author="HR Operations"
        ),
        EvidenceItem(
            source_id="DOC-POL-002",
            title="Remote Work Guidelines",
            category="Information Security",
            excerpt="Hardware allowance covers ergonomic accessories up to $500 per fiscal year.",
            relevance_score=0.88,
            version="3.1",
            author="Security Engineering"
        )
    ]


@pytest.fixture
def sample_analysis(sample_evidence):
    """Provides standardized sample AnalysisResult object."""
    return AnalysisResult(
        key_insights=[
            InsightItem(
                insight_id="INS-TEST-001",
                topic="Human Resources",
                statement="Employees accrue 1.5 days of leave monthly with 10 AM-5 PM core hours.",
                supporting_evidence_ids=["DOC-POL-001"],
                confidence=0.92,
                is_assumption=False
            ),
            InsightItem(
                insight_id="INS-TEST-002",
                topic="Information Security",
                statement="Remote workers are entitled to $500 annual ergonomic hardware reimbursement.",
                supporting_evidence_ids=["DOC-POL-002"],
                confidence=0.88,
                is_assumption=False
            )
        ],
        thematic_clusters={"Human Resources": ["Corporate Leave Policy"], "Information Security": ["Remote Work Guidelines"]},
        cross_document_correlations=["Remote employee policies intersect with corporate hardware guidelines."],
        identified_gaps=[],
        assumptions=[],
        overall_confidence=0.90
    )
