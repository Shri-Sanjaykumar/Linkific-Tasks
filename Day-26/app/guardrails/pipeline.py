"""Unified Responsible AI Pipeline.

Chains Privacy Masking, Fairness Auditing, and Grounding Verification
into an end-to-end Enterprise Guardrail Gateway.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.models import (
    PrivacyScrubResult,
    FairnessMetrics,
    GroundingVerificationResult,
    GuardrailAuditRecord,
)
from app.guardrails.privacy_masker import PrivacyMasker
from app.guardrails.fairness_auditor import FairnessAuditor
from app.guardrails.grounding_verifier import GroundingVerifier


class ResponsibleAIPipeline:
    """Enterprise gateway orchestrating pre-inference and post-inference guardrails."""

    def __init__(self):
        self.privacy_engine = PrivacyMasker()
        self.fairness_engine = FairnessAuditor()
        self.grounding_engine = GroundingVerifier()

    def pre_inference_privacy_gate(self, prompt_text: str) -> PrivacyScrubResult:
        """Sanitizes user prompts and document inputs before sending to LLM APIs."""
        return self.privacy_engine.scrub_text(prompt_text)

    def post_inference_grounding_gate(
        self,
        llm_response: str,
        source_context: str,
    ) -> GroundingVerificationResult:
        """Verifies factual integrity and numerical consistency of LLM responses."""
        return self.grounding_engine.verify_grounding(llm_response, source_context)

    def demographic_fairness_audit_gate(
        self,
        batch_decisions: List[Dict[str, Any]],
        protected_column: str,
        privileged_val: Any,
        unprivileged_val: Any,
    ) -> FairnessMetrics:
        """Audits batch model decisions for compliance with EEOC Disparate Impact Standards."""
        return self.fairness_engine.audit_decisions(
            records=batch_decisions,
            protected_attribute=protected_column,
            privileged_group_value=privileged_val,
            unprivileged_group_value=unprivileged_val,
        )

    def run_full_guardrail_cycle(
        self,
        user_input_with_pii: str,
        simulated_llm_output: str,
        reference_source_doc: str,
        historical_decisions: Optional[List[Dict[str, Any]]] = None,
        protected_col: str = "region",
        privileged_group: str = "Metro",
        unprivileged_group: str = "Rural",
    ) -> Dict[str, Any]:
        """Execute a complete Responsible AI evaluation cycle and generate compliance audit record."""
        # Step 1: Pre-inference Privacy Masking
        privacy_res = self.pre_inference_privacy_gate(user_input_with_pii)

        # Step 2: Post-inference Grounding Verification
        grounding_res = self.post_inference_grounding_gate(simulated_llm_output, reference_source_doc)

        # Step 3: Fairness Auditing
        if historical_decisions:
            fairness_res = self.demographic_fairness_audit_gate(
                batch_decisions=historical_decisions,
                protected_column=protected_col,
                privileged_val=privileged_group,
                unprivileged_val=unprivileged_group,
            )
        else:
            fairness_res = self.fairness_engine.audit_decisions([], protected_col)

        # Step 4: Overall Decision Synthesis
        all_passed = (
            grounding_res.is_grounded and
            (fairness_res.passes_four_fifths_rule if historical_decisions else True)
        )
        violations: List[str] = []
        if not grounding_res.is_grounded:
            violations.extend(grounding_res.unsupported_claims)
        if historical_decisions and not fairness_res.passes_four_fifths_rule:
            violations.extend(fairness_res.violations)

        record_id = f"RAI-AUDIT-{uuid.uuid4().hex[:8].upper()}"
        audit_record = GuardrailAuditRecord(
            record_id=record_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            privacy_passed=True,  # Successfully scrubbed
            privacy_redactions_made=privacy_res.redacted_count,
            grounding_passed=grounding_res.is_grounded,
            citation_score=grounding_res.citation_coverage_score,
            fairness_passed=fairness_res.passes_four_fifths_rule,
            disparate_impact_ratio=fairness_res.disparate_impact_ratio,
            overall_compliance_decision="APPROVED" if all_passed else "REJECTED_ETHICS_VIOLATION",
            violations_summary=violations,
        )

        return {
            "audit_record": audit_record,
            "privacy_result": privacy_res,
            "grounding_result": grounding_res,
            "fairness_result": fairness_res,
        }
