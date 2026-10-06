"""Unit and Integration Tests for Day 25 AI/ML Provider Comparison Benchmark."""

import os
import json
import pytest
from app.models import (
    ProviderEnum,
    ModelTierEnum,
    ModelSpec,
    PricingSpec,
    BenchmarkScores,
    LatencySpec,
    RoutingConstraint,
)
from app.database import (
    MODEL_REGISTRY,
    get_all_models,
    get_model_by_id,
    get_models_by_provider,
)
from app.token_estimator import estimate_tokens, calculate_cache_breakdown
from app.cost_calculator import CostCalculator
from app.latency_simulator import LatencySimulator
from app.router import LLMRouter
from app.client import EvaluationClient


# -------------------------------------------------------------
# Test Database & Models
# -------------------------------------------------------------
def test_all_models_registered():
    models = get_all_models()
    assert len(models) == 8
    providers = {m.provider for m in models}
    assert providers == {
        ProviderEnum.OPENAI,
        ProviderEnum.CLAUDE,
        ProviderEnum.GEMINI,
        ProviderEnum.GROQ,
    }


def test_model_by_id_lookup():
    m = get_model_by_id("gpt-4o")
    assert m.name == "GPT-4o (Omni)"
    assert m.pricing.input_per_m == 2.50
    assert m.pricing.output_per_m == 10.00


def test_invalid_model_lookup_raises():
    with pytest.raises(KeyError):
        get_model_by_id("non-existent-model")


def test_get_models_by_provider():
    groq_models = get_models_by_provider(ProviderEnum.GROQ)
    assert len(groq_models) == 2
    assert any(m.id == "groq-llama-3-3-70b" for m in groq_models)
    assert any(m.id == "groq-llama-3-1-8b" for m in groq_models)


# -------------------------------------------------------------
# Test Token Estimator
# -------------------------------------------------------------
def test_estimate_tokens():
    text = "Hello world! This is a test invoice from Vendor Inc for $5,000.00."
    tokens = estimate_tokens(text)
    assert tokens > 0
    assert tokens < len(text)  # roughly 1/4 of char length


def test_estimate_tokens_empty():
    assert estimate_tokens("") == 0


def test_calculate_cache_breakdown():
    sys_prompt = "You are an enterprise invoice parsing agent. Always output valid RFC 8259 JSON."
    few_shot = "Example 1: Input -> Output JSON.\nExample 2: Input -> Output JSON."
    user_payload = "Invoice #901: $4,500.00 to Staples Inc."
    
    breakdown = calculate_cache_breakdown(
        system_prompt=sys_prompt,
        few_shot_examples=few_shot,
        user_payload=user_payload,
        expected_output_tokens=300,
    )
    assert breakdown["system_tokens"] > 0
    assert breakdown["static_cacheable_prefix_tokens"] > breakdown["dynamic_user_tokens"]
    assert breakdown["cacheable_ratio"] > 0.5


# -------------------------------------------------------------
# Test Cost Calculator
# -------------------------------------------------------------
def test_cost_calculation_gpt4o():
    # 1M input = $2.50, 1M output = $10.00
    gpt4o = get_model_by_id("gpt-4o")
    cost = CostCalculator.calculate_single_call_cost(
        model=gpt4o,
        input_tokens=1_000_000,
        output_tokens=1_000_000,
        cached_input_tokens=0,
    )
    assert abs(cost - 12.50) < 0.0001


def test_cost_calculation_with_prompt_caching():
    claude = get_model_by_id("claude-3-5-sonnet")
    # Fresh input: $3/M, Cached read: $0.30/M (90% savings)
    cost_uncached = CostCalculator.calculate_single_call_cost(
        model=claude,
        input_tokens=100_000,
        output_tokens=1_000,
        cached_input_tokens=0,
    )
    cost_cached = CostCalculator.calculate_single_call_cost(
        model=claude,
        input_tokens=100_000,
        output_tokens=1_000,
        cached_input_tokens=80_000,  # 80k cached
    )
    assert cost_cached < cost_uncached
    # Savings should be significant
    assert (cost_uncached - cost_cached) > 0.15


def test_batch_api_discount():
    gpt4o = get_model_by_id("gpt-4o")
    standard = CostCalculator.calculate_single_call_cost(gpt4o, 1000, 200, is_batch=False)
    batch = CostCalculator.calculate_single_call_cost(gpt4o, 1000, 200, is_batch=True)
    assert abs(batch - (standard * 0.5)) < 0.000001


def test_compare_costs_sorted():
    results = CostCalculator.compare_costs(input_tokens=2000, output_tokens=300)
    assert len(results) == 8
    # Should be sorted ascending by cached cost
    for i in range(len(results) - 1):
        assert results[i].cached_cost_usd <= results[i + 1].cached_cost_usd


def test_enterprise_savings_simulation():
    savings = CostCalculator.estimate_enterprise_savings(
        monthly_docs=10_000,
        avg_input_tokens=2000,
        avg_output_tokens=400,
    )
    assert savings["monthly_savings_usd"] > 0
    assert savings["annual_savings_usd"] == round(savings["monthly_savings_usd"] * 12.0, 2)
    assert savings["cost_reduction_percentage"] > 50.0  # Hybrid router saves >50% vs raw gpt-4o


# -------------------------------------------------------------
# Test Latency Simulator
# -------------------------------------------------------------
def test_latency_groq_vs_claude():
    groq = get_model_by_id("groq-llama-3-1-8b")
    claude = get_model_by_id("claude-3-5-sonnet")
    
    groq_lat = LatencySimulator.calculate_expected_latency(groq, 1000, 200)
    claude_lat = LatencySimulator.calculate_expected_latency(claude, 1000, 200)
    
    # Groq should be substantially faster
    assert groq_lat["total_latency_sec"] < claude_lat["total_latency_sec"]
    assert groq_lat["ttft_sec"] < claude_lat["ttft_sec"]


# -------------------------------------------------------------
# Test Router
# -------------------------------------------------------------
def test_router_prioritizes_speed():
    router = LLMRouter()
    c = RoutingConstraint(max_latency_sec=1.0, priority="speed")
    dec = router.route(1000, 100, c)
    # Groq should win speed constraint
    assert dec.selected_model.provider == ProviderEnum.GROQ


def test_router_prioritizes_accuracy():
    router = LLMRouter()
    c = RoutingConstraint(min_accuracy_percent=94.0, priority="accuracy")
    dec = router.route(1000, 100, c)
    # Claude 3.5 Sonnet has 95.8% accuracy
    assert dec.selected_model.id == "claude-3-5-sonnet"


def test_router_prioritizes_cost():
    router = LLMRouter()
    c = RoutingConstraint(max_cost_per_query_usd=0.0005, priority="cost")
    dec = router.route(1000, 100, c)
    assert dec.selected_model.id in ["groq-llama-3-1-8b", "gemini-2-0-flash"]


# -------------------------------------------------------------
# Test Evaluation Client & Benchmark Dataset
# -------------------------------------------------------------
def test_benchmark_dataset_integrity():
    dataset_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "benchmark_dataset.json")
    assert os.path.exists(dataset_path)
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 20
    for item in data:
        assert "id" in item
        assert "category" in item
        assert "prompt" in item
        assert "expected_keys" in item
        assert "ground_truth" in item


def test_evaluation_client_run():
    dataset_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "benchmark_dataset.json")
    client = EvaluationClient(dataset_path)
    results = client.run_evaluation(model_id="gemini-2-0-flash", sample_limit=5)
    assert len(results) == 5
    for r in results:
        assert r.status == "SUCCESS"
        assert r.cost_usd > 0
        assert r.latency_sec > 0
        assert r.accuracy_score >= 0.80
