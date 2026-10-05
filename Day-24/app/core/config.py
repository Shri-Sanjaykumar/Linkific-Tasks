"""
Linkific Enterprise AI Service - Configuration Management
Loads, validates, and exposes environment variables using Pydantic Settings.
"""

from functools import lru_cache
from typing import List, Dict, Any, Union
import json
import os
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Strongly-typed production settings model.
    Validates environment variables at application startup.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

    # Application Identity
    APP_NAME: str = Field(default="Linkific Enterprise Automation Service", description="Application service name")
    APP_VERSION: str = Field(default="1.0.0", description="Semantic service release version")
    ENVIRONMENT: str = Field(default="development", description="Runtime environment: development, staging, production, test")
    DEBUG: bool = Field(default=False, description="Debug mode flag")

    # Network Runtime
    HOST: str = Field(default="0.0.0.0", description="Binding IP host")
    PORT: int = Field(default=8000, description="Binding HTTP port")
    WORKERS: int = Field(default=1, description="Uvicorn worker count")

    # Security & Access Control
    API_KEY: str = Field(default="linkific-sec-prod-key-2026-xyz", description="Authentication API key")
    CORS_ORIGINS: Union[List[str], str] = Field(
        default=["*"],
        description="Allowed CORS origin domains"
    )

    # Logging Subsystem
    LOG_LEVEL: str = Field(default="INFO", description="Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    LOG_FORMAT: str = Field(default="json", description="Log layout format: json or text")
    LOG_FILE_PATH: str = Field(default="data/service.log", description="Path to active rotating log file")
    LOG_ROTATION_BYTES: int = Field(default=10485760, description="Max bytes per log file (10MB)")
    LOG_BACKUP_COUNT: int = Field(default=5, description="Number of rotated backup log files")

    # Data & Document Ingestion
    DOCS_CORPUS_PATH: str = Field(default="data/company_docs.json", description="Path to enterprise policy corpus")

    # Observability & Governance
    METRICS_ENABLED: bool = Field(default=True, description="Enable Prometheus metrics endpoint")
    RATE_LIMIT_PER_MINUTE: int = Field(default=120, description="Max requests permitted per client per minute")

    # Multi-Agent Workflow Engine
    MAX_WORKFLOW_REVISIONS: int = Field(default=2, description="Circuit breaker for agent critique revisions")
    CRITIC_APPROVAL_THRESHOLD: float = Field(default=0.80, description="Minimum score for critic quality approval")

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"development", "staging", "production", "test"}
        val = v.lower().strip()
        if val not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}, got '{v}'")
        return val

    @field_validator("PORT")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not (1 <= v <= 65535):
            raise ValueError(f"PORT must be between 1 and 65535, got {v}")
        return v

    @field_validator("API_KEY")
    @classmethod
    def validate_api_key(cls, v: str, info) -> str:
        v_clean = v.strip()
        if len(v_clean) < 8:
            raise ValueError("API_KEY must be at least 8 characters long for baseline security")
        return v_clean

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        if isinstance(v, list):
            return v
        return ["*"]

    @property
    def is_production(self) -> bool:
        """Helper to verify if running in production."""
        return self.ENVIRONMENT.lower() == "production"

    def get_safe_dict(self) -> Dict[str, Any]:
        """
        Returns configuration dictionary with secrets safely masked for diagnostics/audit.
        """
        raw = self.model_dump()
        if raw.get("API_KEY"):
            k = raw["API_KEY"]
            if len(k) > 6:
                raw["API_KEY"] = f"{k[:4]}****{k[-3:]}"
            else:
                raw["API_KEY"] = "******"
        return raw


@lru_cache()
def get_settings() -> Settings:
    """
    Cached accessor for application settings.
    Ensures environment configuration is only read once per process.
    """
    return Settings()
