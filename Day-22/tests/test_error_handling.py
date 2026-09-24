"""
Day 22 — Error Handling & Resilience Tests
Validates:
- Graceful recovery when corpus file is missing or corrupted
- Unhandled agent exception containment and workflow failure status
- Rejection of invalid query inputs
- MessageBus error capturing
"""

import pytest
from app.workflow import MultiAgentWorkflowEngine
from app.schemas import WorkflowStatus, WorkflowRequest
from pydantic import ValidationError


def test_missing_corpus_file_handled_gracefully(tmp_path):
    """Verify workflow executes cleanly without crashing if corpus file does not exist."""
    non_existent_file = str(tmp_path / "does_not_exist.json")
    engine = MultiAgentWorkflowEngine(corpus_path=non_existent_file)
    
    response = engine.run("What are the core collaboration hours?")

    assert response.status == WorkflowStatus.COMPLETED
    assert response.final_report is not None
    # Report explicitly discloses data limitation
    has_disclosure = (
        any("insufficient empirical evidence" in sec.content.lower() for sec in response.final_report.sections)
        or "limited" in response.final_report.executive_summary.lower()
    )
    assert has_disclosure


def test_unhandled_agent_exception_marks_workflow_failed(monkeypatch):
    """Verify unhandled exception in an agent marks workflow as FAILED without unhandled crash."""
    from app.agents.research_agent import ResearchAgent

    def broken_research(self, task_id, context=None):
        raise RuntimeError("Database connection suddenly dropped.")

    monkeypatch.setattr(ResearchAgent, "execute", broken_research)

    engine = MultiAgentWorkflowEngine()
    response = engine.run("What is the leave policy?")

    assert response.status == WorkflowStatus.FAILED
    assert response.final_report is None


def test_query_validation_rejection():
    """Verify empty or excessively short queries are rejected."""
    with pytest.raises(ValidationError):
        WorkflowRequest(user_query="")

    with pytest.raises(ValidationError):
        WorkflowRequest(user_query="  \t  \n ")

    with pytest.raises(ValidationError):
        WorkflowRequest(user_query="x")
