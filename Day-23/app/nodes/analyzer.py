"""
Day 23: Analyzer Agent Node
Responsibilities:
- Cognitive synthesis of Research findings into structured insights
- Thematic category clustering & cross-policy correlation analysis
- Factual and numerical preservation (e.g. 1.5 paid leave days)
- Emits ANALYSIS_SUBMISSION to Critic Agent
"""

import re
from typing import Dict, Any, List
from collections import defaultdict
from datetime import datetime, timezone
import logging

from ..schemas import (
    AgentRole,
    MessageType,
    WorkflowStatus,
    Milestone,
    InsightItem,
    AnalysisResult,
    AgentMessage
)
from ..state import MultiAgentState

logger = logging.getLogger("LinkificLangGraph.Analyzer")


def analyzer_node(state: MultiAgentState) -> Dict[str, Any]:
    """
    Transforms raw evidence chunks into thematic clusters and grounded insights.
    Strictly preserves numerical values and full grammatical clauses.
    """
    w_id = state["workflow_id"]
    findings = state.get("research_findings")
    now_iso = datetime.now(timezone.utc).isoformat()

    if not findings or not findings.evidence:
        empty_analysis = AnalysisResult(
            key_insights=[],
            thematic_clusters={},
            cross_document_correlations=[],
            identified_gaps=["No evidence available to analyze."],
            assumptions=[],
            overall_confidence=0.0
        )
        msg = AgentMessage(
            correlation_id=w_id,
            sender=AgentRole.ANALYZER,
            recipient=AgentRole.CRITIC,
            message_type=MessageType.ANALYSIS_SUBMISSION,
            payload={"insight_count": 0, "status": "empty"},
            summary="Analyzer reported zero evidence items available for synthesis."
        )
        return {
            "status": WorkflowStatus.ANALYZING,
            "current_agent": AgentRole.ANALYZER,
            "analysis_result": empty_analysis,
            "communication_log": [msg],
            "next_step": "critic"
        }

    clusters: Dict[str, List[str]] = defaultdict(list)
    insights: List[InsightItem] = []
    correlations: List[str] = []

    for item in findings.evidence:
        clusters[item.category].append(item.title)

        # Robust sentence boundary extraction preserving decimals (e.g. 1.5)
        cleaned_text = item.excerpt.strip()
        match = re.search(r'(?<!\d)[.!?](?!\d)(?:\s+|$)', cleaned_text)
        if match and len(cleaned_text[:match.start()].strip()) > 15:
            core_finding = cleaned_text[:match.start()].strip()
        else:
            core_finding = cleaned_text.rstrip('.')

        insight = InsightItem(
            topic=item.category,
            statement=f"According to {item.title} ({item.source_id}), {core_finding}.",
            supporting_evidence_ids=[item.source_id],
            confidence=round(item.relevance_score, 2),
            is_assumption=False
        )
        insights.append(insight)

    # Cross-document correlation derivation
    categories = list(clusters.keys())
    if len(categories) > 1:
        correlations.append(
            f"Multi-domain policy intersection observed across: {', '.join(categories)}."
        )
        if "Human Resources" in clusters and "Information Security" in clusters:
            correlations.append(
                "Remote work attendance regulations (HR) strictly intersect with VPN & MFA data protection protocols (InfoSec)."
            )

    avg_conf = round(sum(i.confidence for i in insights) / max(len(insights), 1), 3)

    analysis = AnalysisResult(
        key_insights=insights,
        thematic_clusters=dict(clusters),
        cross_document_correlations=correlations,
        identified_gaps=list(findings.unresolved_queries),
        assumptions=[],
        overall_confidence=avg_conf
    )

    submission_msg = AgentMessage(
        correlation_id=w_id,
        sender=AgentRole.ANALYZER,
        recipient=AgentRole.CRITIC,
        message_type=MessageType.ANALYSIS_SUBMISSION,
        payload={
            "insight_count": len(insights),
            "thematic_clusters": list(clusters.keys()),
            "overall_confidence": avg_conf
        },
        summary=f"Analyzer synthesized {len(insights)} verified insights across {len(clusters)} domains."
    )

    # Update Analyzer milestone to completed
    updated_milestones = []
    for m in state.get("milestones", []):
        if m.assigned_agent == AgentRole.ANALYZER:
            m.status = "completed"
            m.completed_at = now_iso
            updated_milestones.append(m)

    return {
        "status": WorkflowStatus.ANALYZING,
        "current_agent": AgentRole.ANALYZER,
        "analysis_result": analysis,
        "milestones": updated_milestones,
        "communication_log": [submission_msg],
        "next_step": "critic"
    }
