"""Enterprise System Configuration & Dual Currency Settings."""

from typing import Dict
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Linkific Enterprise FinDoc-AuditEngine"
    APP_VERSION: str = "3.0.0"
    ENVIRONMENT: str = "production"
    API_V1_STR: str = "/api/v1"

    # Dual currency baseline (1 USD = 86.50 INR)
    USD_TO_INR_RATE: float = 86.50

    # Financial Approval Thresholds in USD
    TIER_1_STP_THRESHOLD_USD: float = 1000.00       # < $1,000 -> Auto STP (< INR 86,500)
    TIER_2_MANAGER_THRESHOLD_USD: float = 10000.00  # $1,000 - $10,000 -> Manager Review (INR 86,500 - 865,000)

    # ML Anomaly Score Thresholds (0 to 100 scale)
    ANOMALY_LOW_MAX_THRESHOLD: float = 35.0
    ANOMALY_HIGH_THRESHOLD: float = 65.0
    ANOMALY_CRITICAL_THRESHOLD: float = 85.0

    # Operational variance tolerances
    MAX_PERMISSIBLE_PRICE_VARIANCE_USD: float = 1.00  # Rounding tolerance
    STANDARD_TAX_MAX_PCT: float = 20.0                # Normal corporate tax ceiling (%)

    # High-Risk Offshore Tax Haven Jurisdictions (ISO-3166)
    OFFSHORE_TAX_HAVENS: list[str] = ["BZ", "VG", "KY", "PA", "BM", "BS", "SC", "VU"]

    # Continuous Sovereign Jurisdiction Risk Weights (0.0 to 1.0)
    JURISDICTION_RISK_MAP: Dict[str, float] = {
        "IN": 0.05,
        "US": 0.05,
        "GB": 0.06,
        "DE": 0.06,
        "SG": 0.08,
        "JP": 0.06,
        "CA": 0.06,
        "AU": 0.06,
        "AE": 0.30,
        "HK": 0.28,
        "CH": 0.22,
        "BZ": 0.95,
        "VG": 0.95,
        "KY": 0.92,
        "PA": 0.90,
        "BM": 0.88,
        "BS": 0.88,
    }

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


settings = Settings()
