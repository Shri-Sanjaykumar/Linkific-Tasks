"""Pydantic data models for Day 25 Enterprise LLM Evaluation Framework."""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field


class ProviderEnum(str, Enum):
    OPENAI = "OpenAI"
    CLAUDE = "Claude"
    GEMINI = "Gemini"
    GROQ = "Groq"


class ModelTierEnum(str, Enum):
    FRONTIER = "frontier"      # High accuracy, complex reasoning
    BALANCED = "balanced"      # Good trade-off
    LIGHTWEIGHT = "fast"       # Ultra fast, low cost


class PricingSpec(BaseModel):
    """Pricing in USD per 1,000,000 tokens."""
    input_per_m: float = Field(..., description="USD per 1M input tokens")
    output_per_m: float = Field(..., description="USD per 1M output tokens")
    cached_input_per_m: Optional[float] = Field(None, description="USD per 1M cached input tokens (prompt cache)")
    batch_discount_ratio: float = Field(0.5, description="Discount multiplier for batch API (e.g. 0.5 = 50% discount)")


class BenchmarkScores(BaseModel):
    """Empirical benchmark scores from official evaluations (Artificial Analysis & LMSYS)."""
    mmlu_score: float = Field(..., description="MMLU / MMLU-Pro accuracy percentage (0-100)")
    humaneval_score: float = Field(..., description="HumanEval coding pass@1 percentage (0-100)")
    gpqa_diamond_score: float = Field(..., description="GPQA Diamond scientific reasoning percentage (0-100)")
    financial_accuracy: float = Field(..., description="Enterprise financial domain extraction accuracy percentage (0-100)")


class LatencySpec(BaseModel):
    """Empirical latency and throughput specs."""
    time_to_first_token_sec: float = Field(..., description="Median TTFT in seconds")
    tokens_per_second: float = Field(..., description="Median generation speed in tokens/second")
    p95_ttft_sec: float = Field(..., description="P95 TTFT in seconds")


class ModelSpec(BaseModel):
    """Complete specification of an LLM provider model."""
    id: str
    provider: ProviderEnum
    name: str
    tier: ModelTierEnum
    context_window: int
    pricing: PricingSpec
    benchmarks: BenchmarkScores
    latency: LatencySpec
    supports_structured_json: bool = True
    supports_prompt_caching: bool = True


class CostCalculationResult(BaseModel):
    """Calculated costs across different traffic volumes and caching conditions."""
    model_id: str
    provider: str
    input_tokens: int
    output_tokens: int
    cache_hit_rate: float
    standard_cost_usd: float
    cached_cost_usd: float
    savings_usd: float
    savings_percent: float
    monthly_cost_standard_usd: float
    monthly_cost_cached_usd: float


class RoutingConstraint(BaseModel):
    """Constraints for model routing."""
    max_cost_per_query_usd: Optional[float] = None
    min_accuracy_percent: Optional[float] = None
    max_latency_sec: Optional[float] = None
    priority: str = Field("balanced", description="One of: 'cost', 'speed', 'accuracy', 'balanced'")


class RoutingDecision(BaseModel):
    """Router decision explaining chosen model."""
    selected_model: ModelSpec
    matched_reason: str
    estimated_cost_usd: float
    estimated_latency_sec: float
    expected_accuracy_percent: float
    candidate_ranking: List[Dict[str, Any]]


class EvaluationResult(BaseModel):
    """Result of running an evaluation test case."""
    test_case_id: str
    category: str
    model_id: str
    provider: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    latency_sec: float
    accuracy_score: float
    matched_ground_truth: bool
    status: str
    details: Dict[str, Any] = Field(default_factory=dict)
