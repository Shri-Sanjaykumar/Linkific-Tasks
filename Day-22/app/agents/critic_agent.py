"""
Day 22 — Critic Agent Implementation
Responsibilities:
- Acts as the adversarial quality gatekeeper for the multi-agent system.
- Audits AnalysisResult and ResearchFindings against factual groundedness and query intent.
- Detects hallucinations, unsupported claims, missing citations, and scope deficiencies.
- Computes empirical quality score and assigns CriticVerdict (APPROVED vs REVISION_REQUIRED).
- Dispatches targeted revision requests with actionable correction directives.
"""

import logging
from typing import List, Dict, Any, Optional
from .base import BaseAgent
from ..schemas import (
    AgentRole,
    MessageType,
    CriticReview,
    CriticVerdict,
    DefectItem,
    DefectCategory,
    DefectSeverity,
    AnalysisResult,
    ResearchFindings
)
from ..config import config

logger = logging.getLogger("LinkificMultiAgent.CriticAgent")


class CriticAgent(BaseAgent):
    """
    Adversarial verification agent enforcing enterprise accuracy and completeness.
    Guarantees zero-hallucination policy and factual traceability before report synthesis.
    """

    def __init__(self, state_manager, bus, min_score: Optional[float] = None):
        super().__init__(AgentRole.CRITIC, state_manager, bus)
        self.min_score = min_score if min_score is not None else config.CRITIC_MIN_SCORE

    def execute(self, task_id: str, context: Optional[Dict[str, Any]] = None) -> CriticReview:
        """
        Conducts systematic audit of SharedState research findings and analysis results.
        Issues approval or specifies actionable defects for iteration.
        """
        self.state_manager.update_agent_status(self.role, self.role, "running")
        snapshot = self.state_manager.get_snapshot()

        query = snapshot.user_query
        findings: Optional[ResearchFindings] = snapshot.research_findings
        analysis: Optional[AnalysisResult] = snapshot.analysis_result
        revision_cycle = snapshot.revision_count

        defects: List[DefectItem] = []
        valid_citations = 0
        total_claims = 0
        unsupported_claims = 0

        # Check 1: Evidence Availability & Source Integrity
        if not findings or not findings.evidence:
            defects.append(DefectItem(
                category=DefectCategory.MISSING_EVIDENCE,
                severity=DefectSeverity.CRITICAL,
                description="Zero evidence items discovered in research phase.",
                target_agent=AgentRole.RESEARCH,
                actionable_correction="Expand search query parameters or broaden semantic matching criteria."
            ))

        # Check 2: Analysis Groundedness & Citation Traceability
        if not analysis or not analysis.key_insights:
            defects.append(DefectItem(
                category=DefectCategory.INCOMPLETE_SCOPE,
                severity=DefectSeverity.CRITICAL,
                description="No analytical insights generated for evaluation.",
                target_agent=AgentRole.ANALYZER,
                actionable_correction="Synthesize at least two grounded insight deductions from available sources."
            ))
        else:
            known_source_ids = {e.source_id for e in findings.evidence} if findings else set()

            for insight in analysis.key_insights:
                total_claims += 1
                if not insight.supporting_evidence_ids:
                    if not insight.is_assumption:
                        unsupported_claims += 1
                        defects.append(DefectItem(
                            category=DefectCategory.UNSUPPORTED_CLAIM,
                            severity=DefectSeverity.MAJOR,
                            description=f"Insight '{insight.statement[:60]}...' lacks supporting evidence references.",
                            target_agent=AgentRole.ANALYZER,
                            actionable_correction="Attach valid source document IDs to the insight or flag explicitly as assumption."
                        ))
                else:
                    # Verify referenced source IDs actually exist in research
                    invalid_ids = [sid for sid in insight.supporting_evidence_ids if sid not in known_source_ids]
                    if invalid_ids:
                        unsupported_claims += 1
                        defects.append(DefectItem(
                            category=DefectCategory.HALLUCINATION,
                            severity=DefectSeverity.CRITICAL,
                            description=f"Insight cites non-existent source IDs: {invalid_ids}.",
                            target_agent=AgentRole.ANALYZER,
                            actionable_correction="Remove phantom citations; bind strictly to retrieved research evidence."
                        ))
                    else:
                        valid_citations += 1

        # Check 3: Query Intent & Scope Coverage
        if query and findings and findings.evidence:
            query_keywords = set(query.lower().split())
            combined_corpus_text = " ".join([e.excerpt.lower() for e in findings.evidence])
            missing_keywords = [kw for kw in query_keywords if len(kw) > 4 and kw not in combined_corpus_text]
            
            # If critical keyword is missing from evidence and this is round 0, request research expansion
            if missing_keywords and revision_cycle == 0 and len(findings.evidence) < 3:
                defects.append(DefectItem(
                    category=DefectCategory.INCOMPLETE_SCOPE,
                    severity=DefectSeverity.MAJOR,
                    description=f"Research evidence may omit coverage for key query concepts: {missing_keywords}.",
                    target_agent=AgentRole.RESEARCH,
                    actionable_correction=f"Execute supplemental search targeting terms: {', '.join(missing_keywords)}."
                ))

        # Metric Calculations
        total_claims_denominator = max(total_claims, 1)
        citation_coverage_pct = round((valid_citations / total_claims_denominator) * 100.0, 1)

        # Base score penalty calculation
        quality_score = 1.0
        for d in defects:
            if d.severity == DefectSeverity.CRITICAL:
                quality_score -= 0.40
            elif d.severity == DefectSeverity.MAJOR:
                quality_score -= 0.15
            elif d.severity == DefectSeverity.MINOR:
                quality_score -= 0.05

        quality_score = max(round(quality_score, 2), 0.0)

        # Verdict Decision
        has_critical = any(d.severity == DefectSeverity.CRITICAL for d in defects)
        
        # If score exceeds threshold and no critical defects, approve
        if quality_score >= self.min_score and not has_critical:
            verdict = CriticVerdict.APPROVED
            summary = f"Quality verification passed with score {quality_score:.2f} ({citation_coverage_pct}% citation coverage)."
        else:
            verdict = CriticVerdict.REVISION_REQUIRED
            summary = (
                f"Quality verification failed with score {quality_score:.2f} (< {self.min_score:.2f}). "
                f"{len(defects)} defect(s) require remediation."
            )

        review = CriticReview(
            verdict=verdict,
            quality_score=quality_score,
            defects=defects,
            citation_coverage_pct=citation_coverage_pct,
            unsupported_claims_count=unsupported_claims,
            feedback_summary=summary,
            revision_cycle=revision_cycle
        )

        # Update Shared State
        self.state_manager.add_critic_review(self.role, review)
        self.state_manager.update_agent_status(self.role, self.role, "completed")

        # Communicate result to Coordinator
        msg_type = MessageType.CRITIC_REVIEW if verdict == CriticVerdict.APPROVED else MessageType.REVISION_REQUEST
        self.send_output(
            task_id=task_id,
            receiver=AgentRole.COORDINATOR,
            message_type=msg_type,
            payload={
                "verdict": verdict.value,
                "quality_score": quality_score,
                "defect_count": len(defects),
                "defects": [d.model_dump() for d in defects]
            }
        )

        return review
