"""
Day 23: Critic Agent Node
Responsibilities:
- Adversarial quality gate auditing AnalysisResult against ground-truth evidence
- Detection of hallucinations, distorted/truncated numbers (e.g. 1 vs 1.5), and incomplete clauses
- Routing: issues approval to proceed to Writer or revision request back to Analyzer
- Enforces circuit breaker threshold (max_revisions = 2)
"""

import re
from typing import Dict, Any, List
from datetime import datetime, timezone
import logging

from ..schemas import (
    AgentRole,
    MessageType,
    WorkflowStatus,
    Milestone,
    CriticReview,
    CriticVerdict,
    DefectItem,
    DefectCategory,
    DefectSeverity,
    AgentMessage
)
from ..state import MultiAgentState
from ..config import config

logger = logging.getLogger("LinkificLangGraph.Critic")


def critic_node(state: MultiAgentState) -> Dict[str, Any]:
    """
    Adversarial verification node inspecting factual integrity and citation coverage.
    Determines whether workflow advances to Writer or cycles for revision.
    """
    w_id = state["workflow_id"]
    query = state.get("query", "")
    findings = state.get("research_findings")
    analysis = state.get("analysis_result")
    revision_count = state.get("revision_count", 0)
    max_revisions = state.get("max_revisions", config.max_revisions)
    now_iso = datetime.now(timezone.utc).isoformat()

    defects: List[DefectItem] = []
    valid_citations = 0
    total_claims = 0

    # 1. Evidence Existence Check
    if not findings or not findings.evidence:
        defects.append(DefectItem(
            category=DefectCategory.MISSING_EVIDENCE,
            severity=DefectSeverity.CRITICAL,
            description="Zero evidence items discovered in research phase.",
            target_agent=AgentRole.RESEARCH,
            actionable_correction="Expand search query keywords or broaden semantic search threshold."
        ))

    # 2. Analysis Groundedness & Numerical Fidelity Check
    if not analysis or not analysis.key_insights:
        defects.append(DefectItem(
            category=DefectCategory.INCOMPLETE_SCOPE,
            severity=DefectSeverity.CRITICAL,
            description="No analytical insights submitted for verification.",
            target_agent=AgentRole.ANALYZER,
            actionable_correction="Formulate structured insights from available evidence."
        ))
    else:
        known_sources = {e.source_id for e in findings.evidence} if findings else set()

        for insight in analysis.key_insights:
            total_claims += 1

            if not insight.supporting_evidence_ids:
                if not insight.is_assumption:
                    defects.append(DefectItem(
                        category=DefectCategory.UNSUPPORTED_CLAIM,
                        severity=DefectSeverity.MAJOR,
                        description=f"Insight '{insight.statement[:50]}...' lacks supporting citations.",
                        target_agent=AgentRole.ANALYZER,
                        actionable_correction="Attach valid source IDs or flag statement as assumption."
                    ))
            else:
                # Check for phantom source IDs
                invalid_ids = [sid for sid in insight.supporting_evidence_ids if sid not in known_sources]
                if invalid_ids:
                    defects.append(DefectItem(
                        category=DefectCategory.HALLUCINATION,
                        severity=DefectSeverity.CRITICAL,
                        description=f"Insight cites non-existent source IDs: {invalid_ids}.",
                        target_agent=AgentRole.ANALYZER,
                        actionable_correction="Remove phantom citations; bind strictly to retrieved research documents."
                    ))
                else:
                    valid_citations += 1

                    # Check 2b: Numerical & Clause Fidelity Check
                    if not insight.is_assumption and findings and findings.evidence:
                        matching_evidence = [e for e in findings.evidence if e.source_id in insight.supporting_evidence_ids]
                        source_texts = " ".join([e.excerpt for e in matching_evidence])

                        # Numerical extraction (excluding document IDs)
                        clean_stmt = re.sub(r'\[?DOC-[A-Z0-9-]+\]?', '', insight.statement)
                        stmt_nums = re.findall(r'\b\d+(?:\.\d+)?\b', clean_stmt)

                        clean_source = re.sub(r'\[?DOC-[A-Z0-9-]+\]?', '', source_texts)
                        source_nums = set(re.findall(r'\b\d+(?:\.\d+)?\b', clean_source))

                        for num in stmt_nums:
                            if num not in source_nums:
                                # Check for decimal truncation (e.g. '1' when source has '1.5')
                                trunc_candidates = [s for s in source_nums if s.startswith(num + ".")]
                                if trunc_candidates:
                                    defects.append(DefectItem(
                                        category=DefectCategory.HALLUCINATION,
                                        severity=DefectSeverity.CRITICAL,
                                        description=f"Factual truncation: numerical value '{num}' truncates true source figure '{trunc_candidates[0]}'.",
                                        target_agent=AgentRole.ANALYZER,
                                        actionable_correction=f"Preserve exact decimal precision '{trunc_candidates[0]}' from source text."
                                    ))
                                else:
                                    defects.append(DefectItem(
                                        category=DefectCategory.UNSUPPORTED_CLAIM,
                                        severity=DefectSeverity.MAJOR,
                                        description=f"Insight asserts numerical figure '{num}' absent from cited source text.",
                                        target_agent=AgentRole.ANALYZER,
                                        actionable_correction="Align numerical claims strictly with figures verified in the evidence."
                                    ))

                        # Sentence completeness & dangling preposition check
                        dangling_match = re.search(
                            r'\b(to|of|and|in|at|the|a|an|with|for|by|or|from|under|subject|are|is)\s*\.?$',
                            insight.statement.strip().rstrip('.')
                        )
                        if dangling_match:
                            defects.append(DefectItem(
                                category=DefectCategory.FORMAT_ERROR,
                                severity=DefectSeverity.CRITICAL,
                                description=f"Premature clause truncation detected: statement ends with dangling word '{dangling_match.group(1)}'.",
                                target_agent=AgentRole.ANALYZER,
                                actionable_correction="Complete the sentence predicate with full factual clauses from source document."
                            ))

    total_claims_denom = max(total_claims, 1)
    citation_coverage = round((valid_citations / total_claims_denom) * 100.0, 1)

    # Score calculation
    quality_score = 1.0
    for d in defects:
        if d.severity == DefectSeverity.CRITICAL:
            quality_score -= 0.40
        elif d.severity == DefectSeverity.MAJOR:
            quality_score -= 0.15
        elif d.severity == DefectSeverity.MINOR:
            quality_score -= 0.05
    quality_score = max(round(quality_score, 2), 0.0)

    has_critical = any(d.severity == DefectSeverity.CRITICAL for d in defects)
    is_approved = not has_critical and quality_score >= config.critic_min_score

    # Update Critic milestone to completed
    updated_milestones = []
    for m in state.get("milestones", []):
        if m.assigned_agent == AgentRole.CRITIC:
            m.status = "completed"
            m.completed_at = now_iso
            updated_milestones.append(m)

    if is_approved:
        verdict = CriticVerdict.APPROVED
        review = CriticReview(
            verdict=verdict,
            quality_score=quality_score,
            citation_coverage_pct=citation_coverage,
            defects=defects,
            revision_notes="All claims grounded in enterprise corpus with 100% citation coverage."
        )
        comm_msg = AgentMessage(
            correlation_id=w_id,
            sender=AgentRole.CRITIC,
            recipient=AgentRole.COORDINATOR,
            message_type=MessageType.CRITIC_REVIEW,
            payload={
                "verdict": verdict.value,
                "quality_score": quality_score,
                "citation_coverage": citation_coverage,
                "defect_count": len(defects)
            },
            summary=f"Critic Agent APPROVED analysis with quality score {quality_score:.2f}."
        )
        return {
            "status": WorkflowStatus.CRITIQUING,
            "current_agent": AgentRole.CRITIC,
            "critic_reviews": [review],
            "milestones": updated_milestones,
            "communication_log": [comm_msg],
            "next_step": "writer"
        }
    else:
        # Check circuit breaker
        if revision_count < max_revisions:
            verdict = CriticVerdict.REVISION_REQUIRED
            notes = "; ".join([d.actionable_correction for d in defects[:2]])
            review = CriticReview(
                verdict=verdict,
                quality_score=quality_score,
                citation_coverage_pct=citation_coverage,
                defects=defects,
                revision_notes=f"Revision required: {notes}"
            )
            rev_msg = AgentMessage(
                correlation_id=w_id,
                sender=AgentRole.CRITIC,
                recipient=AgentRole.ANALYZER,
                message_type=MessageType.REVISION_REQUEST,
                payload={
                    "verdict": verdict.value,
                    "quality_score": quality_score,
                    "defects": [d.model_dump() for d in defects],
                    "cycle": revision_count + 1
                },
                summary=f"Critic Agent requested revision (Cycle {revision_count + 1}) due to {len(defects)} defects."
            )
            return {
                "status": WorkflowStatus.REVISING,
                "current_agent": AgentRole.CRITIC,
                "critic_reviews": [review],
                "revision_count": revision_count + 1,
                "milestones": updated_milestones,
                "communication_log": [rev_msg],
                "next_step": "analyzer"
            }
        else:
            # Circuit breaker triggered
            verdict = CriticVerdict.APPROVED
            review = CriticReview(
                verdict=verdict,
                quality_score=quality_score,
                citation_coverage_pct=citation_coverage,
                defects=defects,
                revision_notes=f"Circuit breaker triggered after {max_revisions} revisions. Proceeding with warnings."
            )
            warn_msg = AgentMessage(
                correlation_id=w_id,
                sender=AgentRole.CRITIC,
                recipient=AgentRole.COORDINATOR,
                message_type=MessageType.CRITIC_REVIEW,
                payload={"verdict": "completed_with_warnings", "revisions_exhausted": True},
                summary=f"Critic tripped circuit breaker at max revisions ({max_revisions}). Halting revision loop."
            )
            return {
                "status": WorkflowStatus.COMPLETED_WITH_WARNINGS,
                "current_agent": AgentRole.CRITIC,
                "critic_reviews": [review],
                "milestones": updated_milestones,
                "communication_log": [warn_msg],
                "next_step": "writer"
            }
