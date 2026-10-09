"""Multi-Tier Financial Approval Router with Dual USD/INR Currency Support."""

import uuid
from datetime import datetime, timezone
from typing import List
from app.models import (
    InvoicePayload,
    MatchResult,
    RiskAssessment,
    AuditDecision,
    ApprovalTierEnum,
    RiskLevelEnum,
)
from app.core.config import settings
from app.core.logging_config import logger


class ApprovalRouter:
    """Routes audited financial transactions to the appropriate corporate governance tier."""

    @classmethod
    def route_decision(
        cls,
        invoice: InvoicePayload,
        match_res: MatchResult,
        risk: RiskAssessment,
        pii_count: int = 0,
    ) -> AuditDecision:
        """Evaluate matching results, ML risk scores, and dollar amounts to determine tier.
        
        Enforces dual currency standard at baseline: 1 USD = 86.50 INR.
        """
        total_usd = float(invoice.total_amount_usd)
        total_inr = round(total_usd * settings.USD_TO_INR_RATE, 2)

        var_usd = float(abs(match_res.price_variance_usd))
        var_inr = round(var_usd * settings.USD_TO_INR_RATE, 2)

        audit_flags: List[str] = []
        audit_flags.extend(match_res.discrepancy_details)
        audit_flags.extend(risk.risk_factors)

        # -------------------------------------------------------------
        # 1. Anomaly & Fraud Defense Filter
        # -------------------------------------------------------------
        if risk.risk_level == RiskLevelEnum.CRITICAL:
            tier = ApprovalTierEnum.FROZEN_FRAUD_RISK
            authorized = False
            requires_hitl = True
            summary = "TRANSACTION FROZEN: Critical ML risk anomaly or offshore structuring detected."

        # -------------------------------------------------------------
        # 2. Reconciliation Discrepancy Filter
        # -------------------------------------------------------------
        elif not match_res.matched:
            tier = ApprovalTierEnum.REJECTED_DISCREPANCY
            authorized = False
            requires_hitl = True
            summary = f"REJECTED: Reconciliation failure. Price/quantity variance of ${var_usd:,.2f} USD (INR {var_inr:,.2f}) detected."

        # -------------------------------------------------------------
        # 3. Clean Reconciliation - Financial Threshold Tiers
        # -------------------------------------------------------------
        elif total_usd < settings.TIER_1_STP_THRESHOLD_USD and risk.risk_level == RiskLevelEnum.LOW:
            # Straight-Through Processing (< $1,000 / < INR 86,500)
            tier = ApprovalTierEnum.TIER_1_STP
            authorized = True
            requires_hitl = False
            summary = f"AUTO-APPROVED (STP): Low-risk compliant invoice below $1,000 USD (INR {total_inr:,.2f})."

        elif total_usd <= settings.TIER_2_MANAGER_THRESHOLD_USD and risk.risk_level in [RiskLevelEnum.LOW, RiskLevelEnum.MEDIUM]:
            # Finance Manager Review ($1,000 - $10,000 / INR 86,500 - 865,000)
            tier = ApprovalTierEnum.TIER_2_MANAGER
            authorized = True
            requires_hitl = True
            summary = f"MANAGER REVIEW REQUIRED: Transaction value ${total_usd:,.2f} USD (INR {total_inr:,.2f}) falls within Tier 2 policy."

        else:
            # Director Signoff (> $10,000 / > INR 865,000 or elevated risk)
            tier = ApprovalTierEnum.TIER_3_DIRECTOR
            authorized = True
            requires_hitl = True
            summary = f"DIRECTOR SIGNOFF REQUIRED: High-value enterprise disbursement of ${total_usd:,.2f} USD (INR {total_inr:,.2f})."

        audit_id = f"AUD-{uuid.uuid4().hex[:8].upper()}"

        logger.info(
            f"Governance Router: Invoice '{invoice.invoice_id}' (${total_usd:,.2f} / INR {total_inr:,.2f}) "
            f"assigned to tier '{tier.value}'."
        )

        return AuditDecision(
            audit_id=audit_id,
            invoice_id=invoice.invoice_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            approval_tier=tier,
            authorized=authorized,
            total_amount_usd=total_usd,
            total_amount_inr=total_inr,
            variance_amount_usd=var_usd,
            variance_amount_inr=var_inr,
            risk_score=risk.anomaly_score,
            risk_level=risk.risk_level,
            requires_hitl=requires_hitl,
            pii_redactions_made=pii_count,
            reconciliation_summary=summary,
            audit_flags=audit_flags,
            feature_contributions=risk.feature_contributions,
        )
