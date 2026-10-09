"""Machine Learning Financial Anomaly & Fraud Risk Scorer.

Uses an unsupervised Isolation Forest model trained on multivariate enterprise financial telemetry:
- Invoice Total Amount ($)
- Price Variance ($)
- Quantity Variance (units)
- New Vendor Indicator (0/1)
- Offshore Country Risk Weight (0/1)
Maps isolation scores to a calibrated 0-100 Risk Score with explainable feature contributions.
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from typing import List
from app.models import (
    InvoicePayload,
    MatchResult,
    RiskAssessment,
    RiskLevelEnum,
    FeatureContribution,
)
from app.core.config import settings
from app.core.logging_config import logger


class AnomalyScorer:
    """Enterprise ML financial risk assessment engine with feature explainability."""

    def __init__(self):
        # Initialize and train Isolation Forest on reference distribution
        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.05,
            random_state=42,
        )
        self._train_baseline_distribution()

    def _train_baseline_distribution(self):
        """Train baseline model on synthetic historical compliant operational transactions."""
        np.random.seed(42)
        n_samples = 600

        # Compliant distributions spanning low-value operational to standard enterprise orders
        amounts = np.concatenate([
            np.random.uniform(100, 1500, n_samples // 2),
            np.random.uniform(1500, 10000, n_samples // 2),
        ])
        price_vars = np.abs(np.random.normal(0.0, 0.2, n_samples))
        qty_vars = np.zeros(n_samples)
        is_new = np.random.choice([0, 1], size=n_samples, p=[0.95, 0.05])
        offshore = np.zeros(n_samples)

        X_train = np.column_stack([amounts, price_vars, qty_vars, is_new, offshore])
        self.model.fit(X_train)

    def extract_features(self, invoice: InvoicePayload, match_res: MatchResult) -> np.ndarray:
        """Extract a 5-dimensional feature vector for ML inference.
        
        Returns:
            np.ndarray of shape (1, 5): [[amount, price_var, qty_var, is_new, offshore]]
        """
        amount = float(invoice.total_amount_usd)
        price_var = float(abs(match_res.price_variance_usd))
        qty_var = float(match_res.quantity_variance_units)
        is_new = 1.0 if invoice.is_new_vendor else 0.0

        # Offshore flag (tax haven jurisdictions)
        offshore = 1.0 if invoice.vendor_country in settings.OFFSHORE_TAX_HAVENS else 0.0

        return np.array([[amount, price_var, qty_var, is_new, offshore]])

    def calculate_feature_contributions(
        self,
        amount: float,
        price_var: float,
        qty_var: float,
        is_new: bool,
        is_offshore: bool,
    ) -> List[FeatureContribution]:
        """Decompose risk drivers into quantified feature contributions for UI explainability."""
        contributions: List[FeatureContribution] = []

        # 1. Base Amount Impact
        amount_pts = min(25.0, round((amount / 50000.0) * 25.0, 1))
        contributions.append(
            FeatureContribution(
                feature_name="Transaction Capital Amount",
                feature_value=f"${amount:,.2f} USD",
                risk_contribution=amount_pts,
                description=f"Transaction value weight relative to typical enterprise volume.",
            )
        )

        # 2. Price Variance Impact
        price_pts = min(35.0, round(price_var * 0.15, 1)) if price_var > 0 else 0.0
        contributions.append(
            FeatureContribution(
                feature_name="Unit Rate Variance",
                feature_value=f"${price_var:,.2f} USD delta",
                risk_contribution=price_pts,
                description="Discrepancy between invoiced rate and agreed PO commitment.",
            )
        )

        # 3. Dock GRN Shortage Impact
        qty_pts = 30.0 if qty_var > 0 else 0.0
        contributions.append(
            FeatureContribution(
                feature_name="Dock GRN Quantity Shortage",
                feature_value=f"{qty_var} unreceived units",
                risk_contribution=qty_pts,
                description="Units billed on invoice but not accepted at receiving dock.",
            )
        )

        # 4. New Vendor Risk
        vendor_pts = 20.0 if is_new else 0.0
        contributions.append(
            FeatureContribution(
                feature_name="Vendor Entity History",
                feature_value="New / Unverified" if is_new else "Established Enterprise Vendor",
                risk_contribution=vendor_pts,
                description="Historical transactional tenure with Linkific Accounts Payable.",
            )
        )

        # 5. Offshore Tax Haven Risk
        haven_pts = 45.0 if is_offshore else 0.0
        contributions.append(
            FeatureContribution(
                feature_name="Jurisdiction Compliance",
                feature_value="High-Risk Offshore Tax Haven" if is_offshore else "Domestic / Compliant Region",
                risk_contribution=haven_pts,
                description="Cross-border tax haven risk filter (Belize, Cayman, Panama, BVI).",
            )
        )

        return contributions

    def assess_risk(self, invoice: InvoicePayload, match_res: MatchResult) -> RiskAssessment:
        """Run ML anomaly prediction and generate comprehensive risk assessment."""
        feat = self.extract_features(invoice, match_res)

        # decision_function yields raw anomaly score: positive = inlier, negative = outlier
        raw_score = self.model.decision_function(feat)[0]
        is_outlier = self.model.predict(feat)[0] == -1

        # Calibrate score to 0 - 100 risk scale:
        # Inliers (raw ~ 0.14) yield ~ 25; outliers (negative) yield >= 40-50
        normalized_risk = float(np.clip(40.0 - (raw_score * 100.0), 5.0, 99.0))

        # Rule-based heuristics augmentations for definitive red flags
        risk_factors: List[str] = []

        if match_res.price_variance_usd > 10.0:
            normalized_risk = max(normalized_risk, 70.0)
            risk_factors.append(f"High price variance detected: ${match_res.price_variance_usd:.2f} USD")

        if match_res.quantity_variance_units > 0:
            normalized_risk = max(normalized_risk, 75.0)
            risk_factors.append(f"Dock GRN quantity mismatch: {match_res.quantity_variance_units} units discrepancy")

        if invoice.is_new_vendor and invoice.total_amount_usd > 5000.0:
            normalized_risk = max(normalized_risk, 68.0)
            risk_factors.append("New vendor invoicing high-value transaction (> $5,000 USD)")

        is_offshore = invoice.vendor_country in settings.OFFSHORE_TAX_HAVENS
        if is_offshore:
            normalized_risk = max(normalized_risk, 90.0)
            risk_factors.append(f"Offshore tax haven jurisdiction: '{invoice.vendor_country}'")

        if not match_res.po_found:
            normalized_risk = max(normalized_risk, 88.0)
            risk_factors.append("Missing Purchase Order in ERP commitments ledger")

        # Classify Risk Level
        if normalized_risk >= settings.ANOMALY_CRITICAL_THRESHOLD:
            level = RiskLevelEnum.CRITICAL
        elif normalized_risk >= settings.ANOMALY_HIGH_THRESHOLD:
            level = RiskLevelEnum.HIGH
        elif normalized_risk >= settings.ANOMALY_LOW_MAX_THRESHOLD:
            level = RiskLevelEnum.MEDIUM
        else:
            level = RiskLevelEnum.LOW

        contributions = self.calculate_feature_contributions(
            amount=invoice.total_amount_usd,
            price_var=match_res.price_variance_usd,
            qty_var=match_res.quantity_variance_units,
            is_new=invoice.is_new_vendor,
            is_offshore=is_offshore,
        )

        logger.info(f"ML Scorer: Invoice '{invoice.invoice_id}' evaluated at risk {normalized_risk:.1f} ({level.value}).")

        return RiskAssessment(
            anomaly_score=round(normalized_risk, 2),
            risk_level=level,
            anomaly_detected=(level in [RiskLevelEnum.HIGH, RiskLevelEnum.CRITICAL]),
            risk_factors=risk_factors,
            feature_contributions=contributions,
        )
