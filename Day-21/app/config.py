"""
Day 21 — Configuration and Environment Settings
Handles typed settings via pydantic-settings.
Adheres strictly to security best practices: NO hardcoded real secrets in code.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Environment identification: 'development', 'testing', or 'production'
    LINKIFIC_ENV: str = "development"

    # API Keys loaded exclusively from environment variables (None by default)
    # Never commit default production or secret keys to source control.
    LINKIFIC_API_KEY: Optional[str] = None
    LINKIFIC_ADMIN_API_KEY: Optional[str] = None

    # Application Configuration
    APP_NAME: str = "Linkific Enterprise AI Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Operational & Resource Limits
    MAX_BATCH_SIZE: int = 10
    QUERY_TIMEOUT_SECONDS: float = 5.0
    DEFAULT_PAGE_LIMIT: int = 20
    MAX_PAGE_LIMIT: int = 100

    # Data & Logging Paths
    DATA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    AUDIT_LOG_FILE: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "activity_audit.jsonl")
    CORPUS_FILE: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sample_docs.json")

    # Benchmark Configuration
    DEFAULT_BENCHMARK_CONCURRENCY: int = 10
    DEFAULT_BENCHMARK_REQUESTS: int = 50

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def is_auth_configured(self) -> bool:
        """Returns True if at least a standard API key is configured."""
        return bool(self.LINKIFIC_API_KEY and self.LINKIFIC_API_KEY.strip())

    def is_admin_auth_configured(self) -> bool:
        """Returns True if an admin API key is configured."""
        return bool(self.LINKIFIC_ADMIN_API_KEY and self.LINKIFIC_ADMIN_API_KEY.strip())


# Global settings singleton
settings = Settings()
