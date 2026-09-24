"""
Day 22 — Critic Revision Loop & Circuit Breaker Tests
Validates:
- Critic-triggered revision requests
- Revision cycle counting and state transitions
- Dynamic re-tasking of Research/Analyzer agents
- Circuit breaker prevention of infinite loops when max revisions are reached
"""

import pytest
from app.workflow import MultiAgentWorkflowEngine
from app.schemas import (
    WorkflowStatus,
    CriticVerdict,
    DefectCategory,
    DefectSeverity,
    DefectItem,
    CriticReview,
    AgentRole
)


def test_revision_loop_triggers_and_resolves(monkeypatch):
    """
    Simulate a scenario where Critic requires revision on cycle 0,
    and approves on cycle 1 after remediation.
    """
    call_count = {"count": 0}

    from app.agents.critic_agent import CriticAgent
    original_execute = CriticAgent.execute

    def mock_critic_execute(self, task_id, context=None):
        call_count["count"] += 1
        if call_count["count"] == 1:
            # First pass: demand revision
            review = CriticReview(
                verdict=CriticVerdict.REVISION_REQUIRED,
                quality_score=0.60,
                defects=[
                    DefectItem(
                        category=DefectCategory.MISSING_EVIDENCE,
                        severity=DefectSeverity.MAJOR,
                        description="Require additional search for remote VPN protocols.",
                        target_agent=AgentRole.RESEARCH,
                        actionable_correction="Search for VPN credentials."
                    )
                ],
                citation_coverage_pct=50.0,
                feedback_summary="Revision required for remote VPN details."
            )
            self.state_manager.add_critic_review(self.role, review)
            return review
        else:
            # Second pass: approve
            return original_execute(self, task_id, context)

    monkeypatch.setattr(CriticAgent, "execute", mock_critic_execute)

    engine = MultiAgentWorkflowEngine(max_revisions=2)
    response = engine.run("What are the remote work and hardware allowance rules?")

    assert response.status == WorkflowStatus.COMPLETED
    assert response.total_revisions == 1
    assert response.critic_approved is True
    assert call_count["count"] >= 2


def test_circuit_breaker_terminates_on_max_revisions(monkeypatch):
    """
    Verify that if Critic continuously rejects, the circuit breaker terminates
    the revision loop at max_revisions and safely completes with warnings.
    """
    from app.agents.critic_agent import CriticAgent

    def permanent_reject(self, task_id, context=None):
        review = CriticReview(
            verdict=CriticVerdict.REVISION_REQUIRED,
            quality_score=0.40,
            defects=[
                DefectItem(
                    category=DefectCategory.HALLUCINATION,
                    severity=DefectSeverity.CRITICAL,
                    description="Unsatisfiable critical policy defect.",
                    target_agent=AgentRole.RESEARCH,
                    actionable_correction="Permanent reject simulation."
                )
            ],
            citation_coverage_pct=20.0,
            feedback_summary="Cannot satisfy criteria."
        )
        self.state_manager.add_critic_review(self.role, review)
        return review

    monkeypatch.setattr(CriticAgent, "execute", permanent_reject)

    max_revisions = 2
    engine = MultiAgentWorkflowEngine(max_revisions=max_revisions)
    response = engine.run("What is the leave policy?")

    assert response.status == WorkflowStatus.COMPLETED
    assert response.total_revisions == max_revisions
    assert response.critic_approved is False
    assert len(response.warnings) > 0
    assert any("circuit breaker" in w.lower() or "max revision" in w.lower() for w in response.warnings)
    # Report was still produced under circuit breaker override
    assert response.final_report is not None
