"""
Day 23: Writer Agent Node
Responsibilities:
- Executive reporting & synthesis
- Inline source attribution [DOC-POL-XXX]
- Construction of Evidence Traceability Matrix
- Supports both streamlined (Coordinator -> Research -> Writer) and comprehensive modes
- Emits REPORT_DRAFT to Coordinator
"""

from typing import Dict, Any, List
from collections import defaultdict
from datetime import datetime, timezone
import re
import logging

from ..schemas import (
    AgentRole,
    MessageType,
    WorkflowStatus,
    Milestone,
    ReportSection,
    WriterReport,
    AgentMessage
)
from ..state import MultiAgentState

logger = logging.getLogger("LinkificLangGraph.Writer")


def writer_node(state: MultiAgentState) -> Dict[str, Any]:
    """
    Synthesizes findings and validated insights into an executive brief.
    Constructs an explicit Evidence Traceability Matrix.
    """
    w_id = state["workflow_id"]
    query = state.get("query", "")
    mode = state.get("mode", "streamlined")
    findings = state.get("research_findings")
    analysis = state.get("analysis_result")
    now_iso = datetime.now(timezone.utc).isoformat()

    title = f"Enterprise Intelligence Brief: {query.strip().rstrip('?')}"
    sections: List[ReportSection] = []
    traceability_matrix: Dict[str, List[str]] = {}

    # Mode 1: Comprehensive Mode (driven by validated analysis_result)
    if mode == "comprehensive" and analysis and analysis.key_insights:
        top_insights = " ".join([i.statement for i in analysis.key_insights[:2]])
        executive_summary = (
            f"This verified enterprise brief addresses the inquiry: '{query}'. "
            f"{top_insights}"
        )

        by_cat = defaultdict(list)
        cat_sources = defaultdict(list)

        for ins in analysis.key_insights:
            cites = " ".join([f"[{sid}]" for sid in ins.supporting_evidence_ids])
            by_cat[ins.topic].append(f"- {ins.statement} {cites}")
            cat_sources[ins.topic].extend(ins.supporting_evidence_ids)
            traceability_matrix[ins.insight_id] = ins.supporting_evidence_ids

        for cat, bullets in by_cat.items():
            sections.append(ReportSection(
                title=f"Policy Dimensions: {cat}",
                content="\n".join(bullets),
                cited_sources=sorted(list(set(cat_sources[cat])))
            ))

    # Mode 2: Streamlined Mode (direct synthesis from research_findings)
    elif findings and findings.evidence:
        first_excerpts = []
        by_cat = defaultdict(list)
        cat_sources = defaultdict(list)

        for item in findings.evidence:
            # Sentence extraction preserving exact numbers (1.5 paid leave days)
            cleaned = item.excerpt.strip()
            match = re.search(r'(?<!\d)[.!?](?!\d)(?:\s+|$)', cleaned)
            if match and len(cleaned[:match.start()].strip()) > 15:
                sent = cleaned[:match.start()].strip()
            else:
                sent = cleaned.rstrip('.')

            statement = f"According to {item.title} ({item.source_id}), {sent}."
            claim_id = f"CLM-{item.source_id.split('-')[-1]}"

            by_cat[item.category].append(f"- {statement} [{item.source_id}]")
            cat_sources[item.category].append(item.source_id)
            traceability_matrix[claim_id] = [item.source_id]
            first_excerpts.append(statement)

        executive_summary = (
            f"This verified enterprise brief addresses the inquiry: '{query}'. "
            f"{' '.join(first_excerpts[:2])}"
        )

        for cat, bullets in by_cat.items():
            sections.append(ReportSection(
                title=f"Policy Dimensions: {cat}",
                content="\n".join(bullets),
                cited_sources=sorted(list(set(cat_sources[cat])))
            ))
    else:
        executive_summary = f"Investigation into '{query}' yielded limited empirical documentation within the corpus."
        sections.append(ReportSection(
            title="Scope & Findings",
            content="No matching enterprise documents were identified for this query.",
            cited_sources=[]
        ))

    limitations = [
        "Analysis is scoped strictly to available documentation in the Linkific enterprise corpus."
    ]
    recommendations = [
        "Ensure cross-departmental alignment prior to executing major policy changes.",
        "Maintain audit logging compliance for all operations intersecting user data or infrastructure.",
        "Subject critical procedural revisions to periodic adversarial review."
    ]

    # Render Markdown output
    md_lines = [
        f"# {title}",
        f"**Workflow ID:** `{w_id}` | **Mode:** `{mode.upper()}` | **Status:** `Verified`\n",
        "## 1. Executive Summary",
        executive_summary,
        ""
    ]
    for sec in sections:
        cites = f" [Cited: {', '.join(sec.cited_sources)}]" if sec.cited_sources else ""
        md_lines.append(f"## {sec.title}{cites}")
        md_lines.append(sec.content)
        md_lines.append("")

    report = WriterReport(
        title=title,
        executive_summary=executive_summary,
        sections=sections,
        evidence_traceability_matrix=traceability_matrix,
        limitations=limitations,
        recommendations=recommendations,
        markdown_output="\n".join(md_lines)
    )

    draft_msg = AgentMessage(
        correlation_id=w_id,
        sender=AgentRole.WRITER,
        recipient=AgentRole.COORDINATOR,
        message_type=MessageType.REPORT_DRAFT,
        payload={
            "report_id": report.report_id,
            "section_count": len(sections),
            "citations": list(traceability_matrix.keys())
        },
        summary=f"Writer Agent synthesized executive report ({report.report_id}) with {len(sections)} sections."
    )

    # Update Writer milestone to completed
    updated_milestones = []
    for m in state.get("milestones", []):
        if m.assigned_agent == AgentRole.WRITER:
            m.status = "completed"
            m.completed_at = now_iso
            updated_milestones.append(m)

    return {
        "status": WorkflowStatus.WRITING,
        "current_agent": AgentRole.WRITER,
        "final_report": report,
        "milestones": updated_milestones,
        "communication_log": [draft_msg],
        "next_step": "coordinator_synthesize"
    }
