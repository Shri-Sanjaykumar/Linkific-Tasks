"""
Day 22 — Multi-Agent System Configuration
Defines environment variables, operational parameters, thresholds, and data paths.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field


class WorkflowConfig(BaseModel):
    """Configuration settings for the Multi-Agent Research Assistant."""

    APP_NAME: str = "Linkific Multi-Agent Research Assistant"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    # Multi-Agent Workflow Controls
    MAX_REVISIONS: int = Field(default=2, description="Maximum revision rounds allowed by Critic")
    CRITIC_MIN_SCORE: float = Field(default=0.80, description="Minimum quality score for Critic approval (0.0 to 1.0)")
    RESEARCH_TOP_K: int = Field(default=4, description="Maximum documents to retrieve during initial research")
    RESEARCH_REVISE_TOP_K: int = Field(default=6, description="Broader retrieval depth during revision rounds")
    SIMILARITY_THRESHOLD: float = Field(default=0.10, description="Minimum keyword/semantic match score")
    WORKFLOW_TIMEOUT_SECONDS: float = Field(default=30.0, description="Global workflow execution timeout")

    # File Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    CORPUS_FILE: str = os.path.join(BASE_DIR, "data", "sample_docs.json")
    AUDIT_LOG_FILE: str = os.path.join(BASE_DIR, "data", "activity_audit.jsonl")


# Global singleton settings
config = WorkflowConfig()
