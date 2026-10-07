"""Algorithmic Fairness and Disparate Impact Auditor.

Evaluates decision outcomes across protected/sensitive demographics.
Calculates Disparate Impact Ratio (DIR) adhering to the EEOC 4/5ths Rule (80% rule),
Demographic Parity Difference, and Equalized Opportunity metrics.
"""

from typing import List, Dict, Any, Optional
from app.models import FairnessMetrics


class FairnessAuditor:
    """Enterprise statistical auditor detecting algorithmic demographic bias."""

    # EEOC standard: unprivileged selection rate / privileged selection rate must be >= 0.80
    FOUR_FIFTHS_THRESHOLD = 0.80

    @classmethod
    def audit_decisions(
        cls,
        records: List[Dict[str, Any]],
        protected_attribute: str,
        favorable_decision_key: str = "approved",
        privileged_group_value: Any = "Group_A",
        unprivileged_group_value: Any = "Group_B",
    ) -> FairnessMetrics:
        """Analyze a collection of automated decision records for demographic disparity."""
        if not records:
            return FairnessMetrics(
                total_evaluated=0,
                group_a_name=str(privileged_group_value),
                group_b_name=str(unprivileged_group_value),
                group_a_approval_rate=0.0,
                group_b_approval_rate=0.0,
                disparate_impact_ratio=1.0,
                demographic_parity_difference=0.0,
                passes_four_fifths_rule=True,
                status="NO_DATA",
                violations=["Empty evaluation dataset"],
            )

        group_a_total = 0
        group_a_approved = 0
        group_b_total = 0
        group_b_approved = 0

        # Confusion matrix stats if ground truth 'actual_qualified' is present
        group_a_true_pos = 0
        group_a_actual_pos = 0
        group_b_true_pos = 0
        group_b_actual_pos = 0

        for r in records:
            group = r.get(protected_attribute)
            decision = bool(r.get(favorable_decision_key))
            actual = r.get("actual_qualified")

            if group == privileged_group_value:
                group_a_total += 1
                if decision:
                    group_a_approved += 1
                if actual is not None:
                    if actual:
                        group_a_actual_pos += 1
                        if decision:
                            group_a_true_pos += 1

            elif group == unprivileged_group_value:
                group_b_total += 1
                if decision:
                    group_b_approved += 1
                if actual is not None:
                    if actual:
                        group_b_actual_pos += 1
                        if decision:
                            group_b_true_pos += 1

        # Calculate selection rates
        rate_a = (group_a_approved / group_a_total) if group_a_total > 0 else 0.0
        rate_b = (group_b_approved / group_b_total) if group_b_total > 0 else 0.0

        # Disparate Impact Ratio = rate_unprivileged / rate_privileged
        if rate_a > 0:
            dir_ratio = rate_b / rate_a
        elif rate_b == 0:
            dir_ratio = 1.0  # both 0
        else:
            dir_ratio = 999.0  # privileged 0, unprivileged > 0

        # Demographic Parity Difference = |rate_a - rate_b|
        dpd = abs(rate_a - rate_b)

        # Equal Opportunity Difference (difference in True Positive Rates)
        eod: Optional[float] = None
        if group_a_actual_pos > 0 and group_b_actual_pos > 0:
            tpr_a = group_a_true_pos / group_a_actual_pos
            tpr_b = group_b_true_pos / group_b_actual_pos
            eod = round(abs(tpr_a - tpr_b), 4)

        passes = (dir_ratio >= cls.FOUR_FIFTHS_THRESHOLD) and (dir_ratio <= 1.25)

        violations: List[str] = []
        if dir_ratio < cls.FOUR_FIFTHS_THRESHOLD:
            violations.append(
                f"Severe Adverse Impact detected: Disparate Impact Ratio {dir_ratio:.3f} is below 0.80 legal threshold (Four-Fifths Rule)."
            )
        elif dir_ratio > 1.25:
            violations.append(
                f"Reverse Disparate Impact detected: Disparate Impact Ratio {dir_ratio:.3f} exceeds 1.25 upper parity bound."
            )

        if dpd > 0.15:
            violations.append(
                f"Demographic Parity Difference {dpd:.3f} exceeds 15% tolerance limit between {privileged_group_value} and {unprivileged_group_value}."
            )

        return FairnessMetrics(
            total_evaluated=len(records),
            group_a_name=str(privileged_group_value),
            group_b_name=str(unprivileged_group_value),
            group_a_approval_rate=round(rate_a, 4),
            group_b_approval_rate=round(rate_b, 4),
            disparate_impact_ratio=round(dir_ratio, 4),
            demographic_parity_difference=round(dpd, 4),
            equal_opportunity_difference=eod,
            passes_four_fifths_rule=passes,
            status="COMPLIANT" if passes else "NON_COMPLIANT_BIASED",
            violations=violations,
        )
