"""
Day 23: Configuration & System Parameters
Linkific Enterprise Multi-Agent System
"""

import os
from pathlib import Path
from pydantic import BaseModel, Field


class SystemConfig(BaseModel):
    """System-wide configuration settings for LangGraph multi-agent execution."""
    base_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent)
    data_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent / "data")
    corpus_file: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent / "data" / "company_docs.json")
    communication_log_file: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent / "data" / "communication_log.json")
    
    max_revisions: int = Field(default=2, description="Circuit breaker threshold for Critic revisions")
    critic_min_score: float = Field(default=0.80, description="Minimum quality score for Critic approval")
    default_top_k: int = Field(default=4, description="Maximum documents to retrieve per query")
    min_evidence_score: float = Field(default=0.10, description="Threshold for evidence relevance filtering")
    
    # Workflow Mode: "streamlined" (Coordinator -> Research -> Writer -> Answer)
    #               or "comprehensive" (Coordinator -> Research -> Analyzer -> Critic -> Writer -> Answer)
    default_workflow_mode: str = Field(default="streamlined", description="Default pipeline execution topology")


config = SystemConfig()
