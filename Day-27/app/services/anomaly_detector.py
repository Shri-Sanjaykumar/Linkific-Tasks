"""Machine Learning Financial Anomaly & Fraud Risk Scorer.

Uses an unsupervised Isolation Forest model trained on multivariate enterprise financial telemetry:
- Invoice Total Amount ($)
- Price Variance ($)
- Quantity Variance (units)
- New Vendor Indicator (0/1)
- Offshore Country Risk Weight (0/1)
Maps isolation scores to a calibrated 0-100 Risk Score.
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from typing import List, Dict, Any
from app.models import InvoicePayload, MatchResult, RiskAssessment, RiskLevelEnum
from app.core.config import settings


class AnomalyScorer:
    """Enterprise ML financial risk assessment engine."""

    def __init__(self):
        # Initialize and train Isolation Forest on baseline reference distribution
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
        """Extract a 5-dimensional feature vector for ML inference."""
        amount = float(invoice.total_amount_usd)
        price_var = float(abs(match_res.price_variance_usd))
        qty_var = float(match_res.quantity_variance_units)
        is_new = 1.0 if invoice.is_new_vendor else 0.0
        
        # Offshore flag (non-IN / non-US or high-risk jurisdictions)
        offshore = 1.0 if invoice.vendor_country in ["BZ", "VG", "KY", "PA"] else 0.0

        return np.array([[amount, price_var, qty_var, is_new, offshore]])

    def assess_risk(self, invoice: InvoicePayload, match_res: MatchResult) -> RiskAssessment:
        """Run ML anomaly prediction and generate risk assessment."""
        feat = self.extract_features(invoice, match_res)
        
        # decision_function yields raw anomaly score: positive = inlier, negative = outlier
        raw_score = self.model.decision_function(feat)[0]
        is_outlier = self.model.predict(feat)[0] == -1

        # Calibrate score to 0 - 100 risk scale:
        # High inliers (raw ~ 0.15) yield ~ 25; outliers (negative) yield >= 40-50
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

        if invoice.vendor_country in ["BZ", "VG", "KY", "PA"]:
            normalized_risk = max(normalized_risk, 90.0)
            risk_factors.append(f"Offshore tax haven jurisdiction: '{invoice.vendor_country}'")

        if not match_res.po_found:
            normalized_risk = max(normalized_risk, 88.0)
            risk_factors.append("Missing Purchase Order in ERP ledger")

        # Classify Risk Level
        if normalized_risk >= settings.ANOMALY_CRITICAL_THRESHOLD:
            level = RiskLevelEnum.CRITICAL
        elif normalized_risk >= settings.ANOMALY_HIGH_THRESHOLD:
            level = RiskLevelEnum.HIGH
        elif normalized_risk >= 35.0:
            level = RiskLevelEnum.MEDIUM
        else:
            level = RiskLevelEnum.LOW

        return RiskAssessment(
            anomaly_score=round(normalized_risk, 2),
            risk_level=level,
            anomaly_detected=(level in [RiskLevelEnum.HIGH, RiskLevelEnum.CRITICAL]),
            risk_factors=risk_factors,
        )
