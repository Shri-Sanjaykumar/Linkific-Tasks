"""Mathematical Cost Optimization Engine for LLM Inference.

Implements exact formulas for:
1. Standard per-token cost
2. KV-Cache Read/Write cost optimization
3. Batch Processing 50% discount
4. Multi-month production volume projections
"""

from typing import Dict, List, Optional
from app.models import ModelSpec, CostCalculationResult
from app.database import MODEL_REGISTRY, get_model_by_id


class CostCalculator:
    """Enterprise LLM Cost Calculation and Optimization Engine."""

    @staticmethod
    def calculate_single_call_cost(
        model: ModelSpec,
        input_tokens: int,
        output_tokens: int,
        cached_input_tokens: int = 0,
        is_batch: bool = False,
    ) -> float:
        """Calculate USD cost for a single query.
        
        Formula:
        cost = [(fresh_input * input_rate) + (cached_input * cached_rate) + (output * output_rate)] / 1,000,000
        """
        fresh_input = max(0, input_tokens - cached_input_tokens)
        
        # Calculate input cost
        fresh_input_cost = (fresh_input * model.pricing.input_per_m) / 1_000_000.0
        
        # Calculate cached input cost
        if cached_input_tokens > 0:
            cached_rate = model.pricing.cached_input_per_m if model.pricing.cached_input_per_m is not None else model.pricing.input_per_m
            cached_input_cost = (cached_input_tokens * cached_rate) / 1_000_000.0
        else:
            cached_input_cost = 0.0

        # Calculate output cost
        output_cost = (output_tokens * model.pricing.output_per_m) / 1_000_000.0

        total_cost = fresh_input_cost + cached_input_cost + output_cost

        # Apply batch discount if applicable
        if is_batch and model.pricing.batch_discount_ratio < 1.0:
            total_cost *= model.pricing.batch_discount_ratio

        return round(total_cost, 7)

    @classmethod
    def compare_costs(
        cls,
        input_tokens: int,
        output_tokens: int,
        cache_hit_rate: float = 0.0,
        monthly_query_volume: int = 100_000,
        is_batch: bool = False,
        model_ids: Optional[List[str]] = None,
    ) -> List[CostCalculationResult]:
        """Compare costs across all models in registry or specified subset."""
        if model_ids is None:
            models = list(MODEL_REGISTRY.values())
        else:
            models = [get_model_by_id(mid) for mid in model_ids]

        results: List[CostCalculationResult] = []

        cached_tokens = int(input_tokens * cache_hit_rate)

        for model in models:
            # Standard cost (0% cache)
            std_cost = cls.calculate_single_call_cost(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cached_input_tokens=0,
                is_batch=is_batch,
            )

            # Cached cost (with given cache_hit_rate)
            cached_cost = cls.calculate_single_call_cost(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cached_input_tokens=cached_tokens,
                is_batch=is_batch,
            )

            savings_usd = std_cost - cached_cost
            savings_pct = (savings_usd / std_cost * 100.0) if std_cost > 0 else 0.0

            monthly_std = std_cost * monthly_query_volume
            monthly_cached = cached_cost * monthly_query_volume

            results.append(
                CostCalculationResult(
                    model_id=model.id,
                    provider=model.provider.value,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cache_hit_rate=cache_hit_rate,
                    standard_cost_usd=std_cost,
                    cached_cost_usd=cached_cost,
                    savings_usd=round(savings_usd, 7),
                    savings_percent=round(savings_pct, 2),
                    monthly_cost_standard_usd=round(monthly_std, 2),
                    monthly_cost_cached_usd=round(monthly_cached, 2),
                )
            )

        # Sort by cached cost ascending (cheapest first)
        results.sort(key=lambda x: x.cached_cost_usd)
        return results

    @classmethod
    def estimate_enterprise_savings(
        cls,
        monthly_docs: int = 50_000,
        avg_input_tokens: int = 2_500,
        avg_output_tokens: int = 400,
        cacheable_prefix_ratio: float = 0.70,
    ) -> Dict[str, Any]:
        """Simulate Linkific enterprise invoice processing savings switching from naive frontier model to hybrid caching architecture."""
        # Baseline: Uncached GPT-4o for 100% of volume
        gpt4o = get_model_by_id("gpt-4o")
        baseline_cost_per_doc = cls.calculate_single_call_cost(gpt4o, avg_input_tokens, avg_output_tokens, 0)
        baseline_monthly = baseline_cost_per_doc * monthly_docs

        # Optimized Hybrid Strategy:
        # - 80% simple extraction routed to Gemini 2.0 Flash with Prompt Caching
        # - 20% complex PO 3-way match routed to Claude 3.5 Sonnet with Prompt Caching
        gemini_flash = get_model_by_id("gemini-2-0-flash")
        claude_sonnet = get_model_by_id("claude-3-5-sonnet")

        cached_tokens = int(avg_input_tokens * cacheable_prefix_ratio)

        gemini_cost = cls.calculate_single_call_cost(gemini_flash, avg_input_tokens, avg_output_tokens, cached_tokens)
        claude_cost = cls.calculate_single_call_cost(claude_sonnet, avg_input_tokens, avg_output_tokens, cached_tokens)

        hybrid_monthly = (0.80 * monthly_docs * gemini_cost) + (0.20 * monthly_docs * claude_cost)
        total_savings_monthly = baseline_monthly - hybrid_monthly
        total_savings_annual = total_savings_monthly * 12.0
        reduction_percentage = (total_savings_monthly / baseline_monthly) * 100.0

        return {
            "monthly_docs": monthly_docs,
            "baseline_model": "gpt-4o (No Caching)",
            "baseline_monthly_usd": round(baseline_monthly, 2),
            "hybrid_monthly_usd": round(hybrid_monthly, 2),
            "monthly_savings_usd": round(total_savings_monthly, 2),
            "annual_savings_usd": round(total_savings_annual, 2),
            "cost_reduction_percentage": round(reduction_percentage, 2),
        }
