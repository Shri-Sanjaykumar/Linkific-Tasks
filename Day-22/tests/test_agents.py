"""
Day 22 — Agent Unit Tests
Tests each of the 5 specialized agents in isolation:
- ResearchAgent retrieval and provenance tracking
- AnalyzerAgent thematic clustering and correlation derivation
- CriticAgent quality scoring, hallucination detection, and defect assignment
- WriterAgent executive briefing synthesis and Evidence Traceability Matrix
- CoordinatorAgent planning and revision evaluation logic
"""

import pytest
from app.schemas import (
    AgentRole,
    CriticVerdict,
    DefectCategory,
    DefectSeverity,
    ResearchFindings,
    EvidenceItem,
    InsightItem,
    AnalysisResult,
    CriticReview,
    WriterReport
)
from app.agents.coordinator_agent import CoordinatorAgent
from app.agents.research_agent import ResearchAgent
from app.agents.analyzer_agent import AnalyzerAgent
from app.agents.critic_agent import CriticAgent
from app.agents.writer_agent import WriterAgent


def test_research_agent_retrieval(state_manager, message_bus):
    """Verify ResearchAgent finds matching documents and populates SharedState."""
    researcher = ResearchAgent(state_manager, message_bus)
    findings = researcher.execute(task_id="TASK-RES-TEST")

    assert findings.status in ("complete", "partial")
    assert len(findings.evidence) > 0
    assert any(e.source_id == "DOC-POL-001" for e in findings.evidence)

    snapshot = state_manager.get_snapshot()
    assert snapshot.research_findings is not None
    assert len(snapshot.research_findings.evidence) == len(findings.evidence)


def test_research_agent_empty_results(state_manager, message_bus):
    """Verify ResearchAgent handles non-existent topics gracefully."""
    # Set query to an unindexed topic
    state_manager._state.user_query = "quantum hyperdrive plasma fusion propulsion"
    researcher = ResearchAgent(state_manager, message_bus)
    findings = researcher.execute(task_id="TASK-RES-EMPTY")

    assert findings.status == "no_results"
    assert len(findings.evidence) == 0
    assert len(findings.unresolved_queries) > 0


def test_analyzer_agent_insight_generation(state_manager, message_bus, sample_evidence):
    """Verify AnalyzerAgent clusters themes and generates grounded insights."""
    state_manager.set_research_findings(
        AgentRole.RESEARCH,
        ResearchFindings(query="test", evidence=sample_evidence)
    )

    analyzer = AnalyzerAgent(state_manager, message_bus)
    analysis = analyzer.execute(task_id="TASK-ANA-TEST")

    assert len(analysis.key_insights) >= 2
    assert "Human Resources" in analysis.thematic_clusters
    assert "Information Security" in analysis.thematic_clusters
    assert analysis.overall_confidence > 0.70

    snapshot = state_manager.get_snapshot()
    assert snapshot.analysis_result is not None


def test_analyzer_agent_empty_evidence_handling(state_manager, message_bus):
    """Verify AnalyzerAgent handles empty research findings without crashing."""
    state_manager.set_research_findings(
        AgentRole.RESEARCH,
        ResearchFindings(query="test", evidence=[])
    )

    analyzer = AnalyzerAgent(state_manager, message_bus)
    analysis = analyzer.execute(task_id="TASK-ANA-EMPTY")

    assert analysis.overall_confidence <= 0.20
    assert len(analysis.identified_gaps) > 0


def test_critic_agent_approves_grounded_analysis(state_manager, message_bus, sample_evidence, sample_analysis):
    """Verify CriticAgent approves grounded analysis with high citation coverage."""
    state_manager.set_research_findings(AgentRole.RESEARCH, ResearchFindings(query="test", evidence=sample_evidence))
    state_manager.set_analysis_result(AgentRole.ANALYZER, sample_analysis)

    critic = CriticAgent(state_manager, message_bus, min_score=0.80)
    review = critic.execute(task_id="TASK-CRI-TEST")

    assert review.verdict == CriticVerdict.APPROVED
    assert review.quality_score >= 0.80
    assert review.citation_coverage_pct == 100.0
    assert not any(d.severity == DefectSeverity.CRITICAL for d in review.defects)


def test_critic_agent_detects_hallucinations(state_manager, message_bus, sample_evidence):
    """Verify CriticAgent catches citations referencing non-existent document IDs."""
    hallucinated_analysis = AnalysisResult(
        key_insights=[
            InsightItem(
                topic="Fantasy Policy",
                statement="All employees get free rockets.",
                supporting_evidence_ids=["DOC-FAKE-999"],  # Phantom citation
                confidence=0.99
            )
        ]
    )

    state_manager.set_research_findings(AgentRole.RESEARCH, ResearchFindings(query="test", evidence=sample_evidence))
    state_manager.set_analysis_result(AgentRole.ANALYZER, hallucinated_analysis)

    critic = CriticAgent(state_manager, message_bus)
    review = critic.execute(task_id="TASK-CRI-HALLUCINATION")

    assert review.verdict == CriticVerdict.REVISION_REQUIRED
    assert any(d.category == DefectCategory.HALLUCINATION for d in review.defects)
    assert any(d.severity == DefectSeverity.CRITICAL for d in review.defects)


def test_writer_agent_report_generation(state_manager, message_bus, sample_evidence, sample_analysis):
    """Verify WriterAgent generates comprehensive brief and Traceability Matrix."""
    state_manager.set_research_findings(AgentRole.RESEARCH, ResearchFindings(query="test", evidence=sample_evidence))
    state_manager.set_analysis_result(AgentRole.ANALYZER, sample_analysis)

    writer = WriterAgent(state_manager, message_bus)
    report = writer.execute(task_id="TASK-WRI-TEST")

    assert report.title.startswith("Enterprise Intelligence Brief:")
    assert len(report.sections) >= 2
    assert len(report.evidence_traceability_matrix) >= 2
    assert "DOC-POL-001" in report.markdown_output
    assert len(report.limitations) > 0
    assert len(report.recommendations) > 0


def test_coordinator_plan_creation(state_manager, message_bus):
    """Verify CoordinatorAgent creates 6-milestone ExecutionPlan."""
    coordinator = CoordinatorAgent(state_manager, message_bus)
    plan = coordinator.execute(task_id="TASK-PLAN-TEST")

    assert len(plan.milestones) == 6
    assert plan.milestones[0].assigned_agent == AgentRole.COORDINATOR
    assert plan.milestones[1].assigned_agent == AgentRole.RESEARCH
    assert plan.milestones[2].assigned_agent == AgentRole.ANALYZER
    assert plan.milestones[3].assigned_agent == AgentRole.CRITIC
    assert plan.milestones[4].assigned_agent == AgentRole.WRITER
    assert plan.milestones[5].assigned_agent == AgentRole.COORDINATOR
