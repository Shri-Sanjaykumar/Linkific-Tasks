"""Multi-Tier Corporate Governance Approval Router with Dual Currency Accounting."""

import uuid
from datetime import datetime, timezone
from typing import Optional
from app.models import (
    InvoicePayload,
    MatchResult,
    RiskAssessment,
    AuditDecision,
    ApprovalTierEnum,
    RiskLevelEnum,
    StageTimingTelemetry,
)
from app.core.config import settings
from app.core.logging_config import logger


class ApprovalRouter:
    """Routes audited invoices across corporate governance tiers with USD & INR pegging."""

    @staticmethod
    def route_decision(
        invoice: InvoicePayload,
        match_res: MatchResult,
        risk: RiskAssessment,
        pii_count: int = 0,
        telemetry: Optional[StageTimingTelemetry] = None,
    ) -> AuditDecision:
        total_usd = round(float(invoice.total_amount_usd), 2)
        total_inr = round(total_usd * settings.USD_TO_INR_RATE, 2)

        var_usd = round(float(match_res.price_variance_usd), 2)
        var_inr = round(var_usd * settings.USD_TO_INR_RATE, 2)

        audit_flags = list(match_res.discrepancy_details) + [
            f for f in risk.risk_factors if f not in match_res.discrepancy_details
        ]

        # 1. Critical Fraud / Compliance Hold
        if risk.risk_level == RiskLevelEnum.CRITICAL:
            tier = ApprovalTierEnum.FROZEN_FRAUD_RISK
            authorized = False
            requires_hitl = True
            summary = (
                f"TRANSACTION FROZEN: Critical ML anomaly score ({risk.anomaly_score:.1f}/100) "
                f"or sovereign compliance flag triggered."
            )

        # 2. Deterministic 3-Way Reconciliation Failure
        elif not match_res.matched:
            tier = ApprovalTierEnum.REJECTED_DISCREPANCY
            authorized = False
            requires_hitl = True
            summary = (
                f"REJECTED: 3-Way reconciliation variance of ${var_usd:,.2f} USD "
                f"(INR {var_inr:,.2f}) across {len(match_res.discrepancy_details)} line-item check(s)."
            )

        # 3. Tier 1: Straight-Through Processing (< $1,000 & Low Risk)
        elif total_usd < settings.TIER_1_STP_THRESHOLD_USD and risk.risk_level == RiskLevelEnum.LOW:
            tier = ApprovalTierEnum.TIER_1_STP
            authorized = True
            requires_hitl = False
            summary = (
                f"AUTO-APPROVED (STP): Compliant 3-way match below $1,000 USD "
                f"(INR {total_inr:,.2f}) with low ML risk ({risk.anomaly_score:.1f})."
            )

        # 4. Tier 2: Finance Manager Review ($1,000 - $10,000 & Low/Medium Risk)
        elif total_usd <= settings.TIER_2_MANAGER_THRESHOLD_USD and risk.risk_level in [
            RiskLevelEnum.LOW,
            RiskLevelEnum.MEDIUM,
        ]:
            tier = ApprovalTierEnum.TIER_2_MANAGER
            authorized = True
            requires_hitl = True
            summary = (
                f"MANAGER REVIEW REQUIRED: Verified transaction of ${total_usd:,.2f} USD "
                f"(INR {total_inr:,.2f}) routed to Finance Manager queue."
            )

        # 5. Tier 3: Executive Director Signoff (> $10,000 or Elevated Risk)
        else:
            tier = ApprovalTierEnum.TIER_3_DIRECTOR
            authorized = True
            requires_hitl = True
            summary = (
                f"DIRECTOR SIGNOFF REQUIRED: High-value or elevated-risk disbursement of "
                f"${total_usd:,.2f} USD (INR {total_inr:,.2f})."
            )

        audit_id = f"AUD-{uuid.uuid4().hex[:8].upper()}"

        logger.info(
            f"Governance Router: Invoice '{invoice.invoice_id}' (${total_usd:,.2f} / INR {total_inr:,.2f}) "
            f"assigned to tier '{tier.value}'."
        )

        return AuditDecision(
            audit_id=audit_id,
            invoice_id=invoice.invoice_id,
            vendor_name=invoice.vendor_name,
            vendor_country=invoice.vendor_country,
            po_number=invoice.po_number,
            timestamp=datetime.now(timezone.utc).isoformat(),
            approval_tier=tier,
            authorized=authorized,
            total_amount_usd=total_usd,
            total_amount_inr=total_inr,
            variance_amount_usd=var_usd,
            variance_amount_inr=var_inr,
            quantity_variance_units=match_res.quantity_variance_units,
            risk_score=risk.anomaly_score,
            risk_level=risk.risk_level,
            requires_hitl=requires_hitl,
            pii_redactions_made=pii_count,
            reconciliation_summary=summary,
            audit_flags=audit_flags,
            feature_contributions=risk.feature_contributions,
            item_diffs=match_res.item_diffs,
            telemetry=telemetry,
        )
