"""
Day 22 — End-to-End Workflow Integration Tests
Validates the full collaborative workflow across multiple enterprise scenarios:
- Successful happy-path execution
- Milestone progression
- Final report generation with grounded citations
- Audit event generation
"""

import pytest
from app.workflow import MultiAgentWorkflowEngine
from app.schemas import WorkflowStatus


def test_workflow_end_to_end_hr_and_security():
    """Verify complete workflow execution for remote work and hardware allowance query."""
    engine = MultiAgentWorkflowEngine()
    query = "What are the corporate guidelines regarding remote work, hardware allowances, and core collaboration hours?"
    
    response = engine.run(query=query)

    assert response.status == WorkflowStatus.COMPLETED
    assert response.workflow_id.startswith("WF-")
    assert response.critic_approved is True
    assert response.final_report is not None
    assert response.execution_time_seconds > 0.0
    assert response.audit_events_count >= 4

    # Verify report contents
    report = response.final_report
    assert "Enterprise Intelligence Brief" in report.title
    assert len(report.sections) >= 2
    assert "DOC-POL-001" in report.markdown_output
    assert len(report.evidence_traceability_matrix) > 0


def test_workflow_end_to_end_engineering_and_qa():
    """Verify complete workflow execution for engineering CI/CD and QA benchmarking query."""
    engine = MultiAgentWorkflowEngine()
    query = "What are the engineering onboarding protocols, peer review requirements, and QA latency performance SLAs?"

    response = engine.run(query=query)

    assert response.status == WorkflowStatus.COMPLETED
    assert response.critic_approved is True
    assert response.final_report is not None

    report = response.final_report
    assert any(s.title.startswith("Policy Dimensions: Engineering") for s in report.sections)
    assert any(s.title.startswith("Policy Dimensions: Quality Assurance") for s in report.sections)


def test_workflow_end_to_end_ai_and_incident_response():
    """Verify complete workflow execution for AI safety and SRE post-mortem query."""
    engine = MultiAgentWorkflowEngine()
    query = "What are our mandatory AI safety principles, human oversight escalation triggers, and Sev-1 incident post-mortem requirements?"

    response = engine.run(query=query)

    assert response.status == WorkflowStatus.COMPLETED
    assert response.critic_approved is True
    assert response.final_report is not None
    assert "DOC-POL-006" in response.final_report.markdown_output
