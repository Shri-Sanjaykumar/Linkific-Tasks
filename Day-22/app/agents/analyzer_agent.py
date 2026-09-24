"""
Day 22 — Analyzer Agent Implementation
Responsibilities:
- Synthesizes Research Agent findings into thematic clusters.
- Distinguishes grounded factual insights from inferences or assumptions.
- Establishes explicit traceability linking each insight to source document IDs.
- Surfaces cross-document correlations and flags policy gaps.
- Submits structured AnalysisResult into Shared State and notifies Critic Agent.
"""

import logging
import re
from typing import List, Dict, Any, Optional
from collections import defaultdict
from .base import BaseAgent
from ..schemas import (
    AgentRole,
    MessageType,
    AnalysisResult,
    InsightItem,
    ResearchFindings
)

logger = logging.getLogger("LinkificMultiAgent.AnalyzerAgent")


class AnalyzerAgent(BaseAgent):
    """
    Cognitive analysis agent transforming raw evidence into structured, verifiable insights.
    """

    def __init__(self, state_manager, bus):
        super().__init__(AgentRole.ANALYZER, state_manager, bus)

    def execute(self, task_id: str, context: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """
        Processes evidence from SharedState, performing thematic clustering,
        correlation analysis, and insight derivation.
        """
        self.state_manager.update_agent_status(self.role, self.role, "running")
        snapshot = self.state_manager.get_snapshot()

        findings: Optional[ResearchFindings] = snapshot.research_findings
        if not findings or not findings.evidence:
            logger.warning("AnalyzerAgent executed without available research evidence.")
            empty_analysis = AnalysisResult(
                key_insights=[
                    InsightItem(
                        topic="Data Availability",
                        statement="Insufficient empirical evidence discovered in enterprise corpus to satisfy the inquiry.",
                        supporting_evidence_ids=[],
                        confidence=0.10,
                        is_assumption=True
                    )
                ],
                identified_gaps=["No grounded documentation retrieved for the requested query topics."],
                overall_confidence=0.10
            )
            self.state_manager.set_analysis_result(self.role, empty_analysis)
            self.state_manager.update_agent_status(self.role, self.role, "completed")
            self.send_output(
                task_id=task_id,
                receiver=AgentRole.CRITIC,
                message_type=MessageType.ANALYSIS_SUBMISSION,
                payload={"status": "empty_evidence", "insight_count": 0}
            )
            return empty_analysis

        # Thematic clustering based on evidence categories
        clusters: Dict[str, List[str]] = defaultdict(list)
        insights: List[InsightItem] = []
        correlations: List[str] = []
        gaps: List[str] = list(findings.unresolved_queries)
        assumptions: List[str] = []

        # Analyze each evidence item
        for item in findings.evidence:
            clusters[item.category].append(item.title)
            
            # Formulate structured insight with robust sentence boundary detection
            # Preserves decimals (e.g. 1.5), percentages, and full clauses
            match = re.search(r'(?<!\d)[.!?](?!\d)(?:\s+|$)', item.excerpt.strip())
            if match and len(item.excerpt[:match.start()].strip()) > 15:
                core_finding = item.excerpt[:match.start()].strip()
            else:
                core_finding = item.excerpt.strip().rstrip('.')
            
            insight = InsightItem(
                topic=item.category,
                statement=f"According to {item.title} ({item.source_id}), {core_finding}.",
                supporting_evidence_ids=[item.source_id],
                confidence=round(item.relevance_score, 2),
                is_assumption=False
            )
            insights.append(insight)

        # Cross-document correlation detection
        categories = list(clusters.keys())
        if len(categories) > 1:
            correlations.append(
                f"Multi-domain policy intersection observed between {', '.join(categories)}."
            )
            # Example cross-policy insight
            if "Human Resources" in clusters and "Information Security" in clusters:
                correlations.append(
                    "Remote attendance guidelines (HR) strictly intersect with VPN & MFA data security protocols (InfoSec)."
                )

        # Add explicit inference/assumption if evidence was sparse
        if len(findings.evidence) < 2:
            assumptions.append(
                "Sparse evidence base: broader organizational directives are assumed to align with general industry standards."
            )
            insights.append(
                InsightItem(
                    topic="Scope Constraint",
                    statement="Analysis relies on a single discovered source; supplemental guidelines may exist.",
                    supporting_evidence_ids=[findings.evidence[0].source_id],
                    confidence=0.60,
                    is_assumption=True
                )
            )

        avg_confidence = round(sum(i.confidence for i in insights) / max(len(insights), 1), 3)

        analysis = AnalysisResult(
            key_insights=insights,
            thematic_clusters=dict(clusters),
            cross_document_correlations=correlations,
            identified_gaps=gaps,
            assumptions=assumptions,
            overall_confidence=avg_confidence
        )

        # Update Shared State
        self.state_manager.set_analysis_result(self.role, analysis)
        self.state_manager.update_agent_status(self.role, self.role, "completed")

        # Forward output to Critic Agent for review
        self.send_output(
            task_id=task_id,
            receiver=AgentRole.CRITIC,
            message_type=MessageType.ANALYSIS_SUBMISSION,
            payload={
                "insight_count": len(insights),
                "thematic_categories": list(clusters.keys()),
                "overall_confidence": avg_confidence
            },
            evidence_ids=[e.source_id for e in findings.evidence]
        )

        return analysis
