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
import re
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


def test_numerical_and_factual_preservation(state_manager, message_bus):
    """
    Verify factual fidelity: decimal quantities (e.g. 1.5 paid leave days)
    are accurately preserved from raw evidence through Analyzer, Critic, and Writer.
    Ensures no truncation occurs from '1.5' to '1.'.
    """
    evidence = [
        EvidenceItem(
            source_id="DOC-POL-001",
            title="Corporate Leave Policy",
            category="Human Resources",
            excerpt="All Linkific employees and interns are entitled to 1.5 paid leave days per completed calendar month of active service. Core collaboration hours are 10:00 AM to 5:00 PM IST.",
            relevance_score=0.95,
            version="2.4",
            author="HR Operations"
        )
    ]
    state_manager.set_research_findings(AgentRole.RESEARCH, ResearchFindings(query="leave entitlement", evidence=evidence))

    # 1. Analyzer Step
    analyzer = AnalyzerAgent(state_manager, message_bus)
    analysis = analyzer.execute(task_id="TASK-ANA-FACTUAL")

    assert len(analysis.key_insights) >= 1
    hr_insight = analysis.key_insights[0]
    assert "1.5" in hr_insight.statement
    assert not re.search(r'entitled to 1\.(?!\d)', hr_insight.statement)
    assert "1.5 paid leave days" in hr_insight.statement

    # 2. Critic Step
    critic = CriticAgent(state_manager, message_bus, min_score=0.80)
    review = critic.execute(task_id="TASK-CRI-FACTUAL")
    assert review.verdict == CriticVerdict.APPROVED
    assert not any(d.severity == DefectSeverity.CRITICAL for d in review.defects)

    # 3. Writer Step
    writer = WriterAgent(state_manager, message_bus)
    report = writer.execute(task_id="TASK-WRI-FACTUAL")
    assert "1.5" in report.executive_summary or "1.5" in report.markdown_output
    assert "1.5 paid leave days" in report.markdown_output
    assert not re.search(r'entitled to 1\.(?!\d)', report.markdown_output)


def test_critic_detects_numerical_truncation_distortion(state_manager, message_bus, sample_evidence):
    """
    Verify CriticAgent actively catches and rejects factual numerical truncation
    (e.g., claiming entitlement of '1' when source evidence explicitly specifies '1.5').
    """
    truncated_analysis = AnalysisResult(
        key_insights=[
            InsightItem(
                topic="Human Resources",
                statement="All Linkific employees and interns are entitled to 1. [DOC-POL-001]",
                supporting_evidence_ids=["DOC-POL-001"],
                confidence=0.90
            )
        ]
    )

    state_manager.set_research_findings(AgentRole.RESEARCH, ResearchFindings(query="leave policy", evidence=sample_evidence))
    state_manager.set_analysis_result(AgentRole.ANALYZER, truncated_analysis)

    critic = CriticAgent(state_manager, message_bus)
    review = critic.execute(task_id="TASK-CRI-TRUNC-CHECK")

    assert review.verdict == CriticVerdict.REVISION_REQUIRED
    # Must flag factual truncation defect
    truncation_defects = [
        d for d in review.defects
        if d.category in (DefectCategory.HALLUCINATION, DefectCategory.FORMAT_ERROR)
        and d.severity == DefectSeverity.CRITICAL
    ]
    assert len(truncation_defects) > 0
    assert any("truncat" in d.description.lower() for d in truncation_defects)


def test_critic_detects_dangling_truncated_clauses(state_manager, message_bus, sample_evidence):
    """
    Verify CriticAgent catches incomplete clauses ending with dangling grammatical prepositions.
    """
    dangling_analysis = AnalysisResult(
        key_insights=[
            InsightItem(
                topic="Human Resources",
                statement="Employees may work from home subject to.",
                supporting_evidence_ids=["DOC-POL-001"],
                confidence=0.85
            )
        ]
    )

    state_manager.set_research_findings(AgentRole.RESEARCH, ResearchFindings(query="remote work", evidence=sample_evidence))
    state_manager.set_analysis_result(AgentRole.ANALYZER, dangling_analysis)

    critic = CriticAgent(state_manager, message_bus)
    review = critic.execute(task_id="TASK-CRI-DANGLING-CHECK")

    assert review.verdict == CriticVerdict.REVISION_REQUIRED
    assert any(d.category == DefectCategory.FORMAT_ERROR for d in review.defects)
