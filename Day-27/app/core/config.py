"""System Configuration & Dual Currency Settings."""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Linkific Enterprise FinDoc-AuditEngine"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "production"
    API_V1_STR: str = "/api/v1"
    
    # Dual currency baseline (1 USD = 86.50 INR)
    USD_TO_INR_RATE: float = 86.50
    
    # Financial Approval Thresholds in USD
    TIER_1_STP_THRESHOLD_USD: float = 1000.00       # < $1,000 -> Auto STP
    TIER_2_MANAGER_THRESHOLD_USD: float = 10000.00  # $1,000 - $10,000 -> Manager Review
    # > $10,000 -> Director Signoff
    
    # ML Anomaly Score Thresholds (0 to 100 scale)
    ANOMALY_HIGH_THRESHOLD: float = 65.0
    ANOMALY_CRITICAL_THRESHOLD: float = 85.0
    
    # Tolerance thresholds for price variance
    MAX_PERMISSIBLE_PRICE_VARIANCE_USD: float = 1.00  # Rounding tolerance

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


settings = Settings()
