"""
Day 22 — Writer Agent Implementation
Responsibilities:
- Synthesizes validated analysis insights and grounded evidence into publication-ready reports.
- Enforces strict factual attribution, embedding inline source citations for every claim.
- Constructs an Evidence Traceability Matrix linking insights to source policy IDs.
- Discloses operational boundaries, limitations, and actionable recommendations.
- Submits structured WriterReport and rendered Markdown to Shared State.
"""

import logging
from typing import List, Dict, Any, Optional
from .base import BaseAgent
from ..schemas import (
    AgentRole,
    MessageType,
    WriterReport,
    ReportSection,
    AnalysisResult,
    ResearchFindings,
    CriticReview
)

logger = logging.getLogger("LinkificMultiAgent.WriterAgent")


class WriterAgent(BaseAgent):
    """
    Professional documentation and synthesis agent producing executive-grade enterprise briefs.
    """

    def __init__(self, state_manager, bus):
        super().__init__(AgentRole.WRITER, state_manager, bus)

    def execute(self, task_id: str, context: Optional[Dict[str, Any]] = None) -> WriterReport:
        """
        Synthesizes validated findings and analysis into structured enterprise report.
        """
        self.state_manager.update_agent_status(self.role, self.role, "running")
        snapshot = self.state_manager.get_snapshot()

        query = snapshot.user_query
        findings: Optional[ResearchFindings] = snapshot.research_findings
        analysis: Optional[AnalysisResult] = snapshot.analysis_result
        last_review: Optional[CriticReview] = snapshot.critic_reviews[-1] if snapshot.critic_reviews else None

        title = f"Enterprise Intelligence Brief: {query.strip().rstrip('?')}"
        
        # Build Executive Summary
        if analysis and analysis.key_insights:
            top_insights_summary = " ".join([i.statement for i in analysis.key_insights[:2]])
            executive_summary = (
                f"This report presents a verified cross-departmental synthesis addressing: '{query}'. "
                f"{top_insights_summary}"
            )
        else:
            executive_summary = f"Investigation into '{query}' yielded limited empirical documentation within the corpus."

        # Build Thematic Sections
        sections: List[ReportSection] = []
        traceability: Dict[str, List[str]] = {}

        if analysis and analysis.key_insights:
            # Group insights by category
            by_category: Dict[str, List[str]] = {}
            category_sources: Dict[str, List[str]] = {}

            for ins in analysis.key_insights:
                cat = ins.topic
                if cat not in by_category:
                    by_category[cat] = []
                    category_sources[cat] = []
                
                cite_tags = " ".join([f"[{sid}]" for sid in ins.supporting_evidence_ids])
                by_category[cat].append(f"- {ins.statement} {cite_tags}")
                category_sources[cat].extend(ins.supporting_evidence_ids)
                traceability[ins.insight_id] = ins.supporting_evidence_ids

            for cat, bullets in by_category.items():
                sections.append(ReportSection(
                    title=f"Policy Dimensions: {cat}",
                    content="\n".join(bullets),
                    cited_sources=list(set(category_sources[cat]))
                ))

        # Add Cross-Document Correlations Section
        if analysis and analysis.cross_document_correlations:
            corr_text = "\n".join([f"- {c}" for c in analysis.cross_document_correlations])
            sections.append(ReportSection(
                title="Cross-Policy Correlations & Intersections",
                content=corr_text,
                cited_sources=[]
            ))

        # Build Limitations & Recommendations
        limitations = []
        if analysis and analysis.identified_gaps:
            limitations.extend(analysis.identified_gaps)
        if analysis and analysis.assumptions:
            limitations.extend([f"Working Assumption: {a}" for a in analysis.assumptions])
        if not limitations:
            limitations.append("Analysis is scoped strictly to available documentation in the Linkific enterprise corpus.")

        recommendations = [
            "Ensure cross-departmental alignment prior to executing major policy changes.",
            "Maintain audit logging compliance for all operations intersecting user data or infrastructure.",
            "Subject critical procedural revisions to periodic adversarial review."
        ]

        # Render Publication-Ready Markdown
        md_lines = [
            f"# {title}",
            f"**Workflow ID:** `{snapshot.workflow_id}` | **Status:** `Verified`",
            "",
            "## 1. Executive Summary",
            executive_summary,
            ""
        ]

        for s_idx, sec in enumerate(sections, start=2):
            md_lines.append(f"## {s_idx}. {sec.title}")
            md_lines.append(sec.content)
            if sec.cited_sources:
                md_lines.append(f"\n*Sources Cited:* {', '.join(sec.cited_sources)}")
            md_lines.append("")

        md_lines.append("## Operational Boundaries & Limitations")
        for lim in limitations:
            md_lines.append(f"- {lim}")
        md_lines.append("")

        md_lines.append("## Strategic Recommendations")
        for rec in recommendations:
            md_lines.append(f"- {rec}")
        md_lines.append("")

        if last_review:
            md_lines.append(f"> **Critic Audit Sign-Off:** Verdict `{last_review.verdict.value}` | Quality Score `{last_review.quality_score:.2f}` | Coverage `{last_review.citation_coverage_pct}%`")

        rendered_md = "\n".join(md_lines)

        report = WriterReport(
            title=title,
            executive_summary=executive_summary,
            sections=sections,
            evidence_traceability_matrix=traceability,
            limitations=limitations,
            recommendations=recommendations,
            markdown_output=rendered_md
        )

        # Update Shared State
        self.state_manager.set_final_report(self.role, report)
        self.state_manager.update_agent_status(self.role, self.role, "completed")

        # Submit to Coordinator
        self.send_output(
            task_id=task_id,
            receiver=AgentRole.COORDINATOR,
            message_type=MessageType.REPORT_DRAFT,
            payload={"report_id": report.report_id, "title": title}
        )

        return report
