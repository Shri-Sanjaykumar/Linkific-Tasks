"""Pareto-Optimal Multi-Objective LLM Router.

Routes incoming queries to the optimal provider and model based on:
- Latency SLA (maximum tolerable delay)
- Cost budget (maximum dollar threshold per call)
- Accuracy requirement (minimum benchmark score for the domain)
- Task complexity (simple extraction vs complex reasoning)
"""

from typing import List, Dict, Any, Optional
from app.models import (
    ModelSpec,
    RoutingConstraint,
    RoutingDecision,
)
from app.database import MODEL_REGISTRY
from app.cost_calculator import CostCalculator
from app.latency_simulator import LatencySimulator


class LLMRouter:
    """Intelligent SLA-driven Multi-Provider Model Router."""

    def __init__(self, models: Optional[List[ModelSpec]] = None):
        self.models = models or list(MODEL_REGISTRY.values())

    def route(
        self,
        input_tokens: int,
        output_tokens: int,
        constraints: RoutingConstraint,
        cached_input_tokens: int = 0,
    ) -> RoutingDecision:
        """Evaluate candidate models and pick optimal model adhering to constraints."""
        evaluated_candidates: List[Dict[str, Any]] = []

        for model in self.models:
            cost = CostCalculator.calculate_single_call_cost(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cached_input_tokens=cached_input_tokens,
            )
            lat_metrics = LatencySimulator.calculate_expected_latency(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
            total_lat = lat_metrics["total_latency_sec"]
            acc = model.benchmarks.financial_accuracy

            # Hard Constraint Filtering
            violates_cost = (constraints.max_cost_per_query_usd is not None and cost > constraints.max_cost_per_query_usd)
            violates_lat = (constraints.max_latency_sec is not None and total_lat > constraints.max_latency_sec)
            violates_acc = (constraints.min_accuracy_percent is not None and acc < constraints.min_accuracy_percent)

            is_eligible = not (violates_cost or violates_lat or violates_acc)

            # Composite Score based on priority
            # Normalize:
            # - cost (lower is better): cost_score = 1.0 / (1.0 + cost * 1000)
            # - latency (lower is better): lat_score = 1.0 / (1.0 + total_lat)
            # - accuracy (higher is better): acc_score = acc / 100.0
            cost_score = 1.0 / (1.0 + cost * 1000)
            lat_score = 1.0 / (1.0 + total_lat)
            acc_score = acc / 100.0

            if constraints.priority == "cost":
                composite_score = (0.70 * cost_score) + (0.15 * lat_score) + (0.15 * acc_score)
            elif constraints.priority == "speed":
                composite_score = (0.15 * cost_score) + (0.70 * lat_score) + (0.15 * acc_score)
            elif constraints.priority == "accuracy":
                composite_score = (0.10 * cost_score) + (0.15 * lat_score) + (0.75 * acc_score)
            else:  # balanced
                composite_score = (0.33 * cost_score) + (0.33 * lat_score) + (0.34 * acc_score)

            evaluated_candidates.append({
                "model_id": model.id,
                "provider": model.provider.value,
                "name": model.name,
                "cost_usd": cost,
                "latency_sec": total_lat,
                "accuracy_percent": acc,
                "is_eligible": is_eligible,
                "composite_score": round(composite_score, 4),
                "model_ref": model,
            })

        # Filter eligible candidates; if none meet all hard constraints, fall back to best overall composite
        eligible = [c for c in evaluated_candidates if c["is_eligible"]]
        if not eligible:
            fallback = sorted(evaluated_candidates, key=lambda x: x["composite_score"], reverse=True)[0]
            matched_reason = "Relaxed constraints fallback (no single model met all strict SLA filters)"
            winner = fallback
        else:
            sorted_eligible = sorted(eligible, key=lambda x: x["composite_score"], reverse=True)
            winner = sorted_eligible[0]
            matched_reason = f"Optimal candidate selected under priority '{constraints.priority}'"

        # Prepare ranking list without model_ref object for serialization
        clean_ranking = [
            {
                "model_id": c["model_id"],
                "provider": c["provider"],
                "name": c["name"],
                "cost_usd": c["cost_usd"],
                "latency_sec": c["latency_sec"],
                "accuracy_percent": c["accuracy_percent"],
                "is_eligible": c["is_eligible"],
                "composite_score": c["composite_score"],
                "cost_inr": round(c["cost_usd"] * 86.50, 4),
            }
            for c in sorted(evaluated_candidates, key=lambda x: x["composite_score"], reverse=True)
        ]

        return RoutingDecision(
            selected_model=winner["model_ref"],
            matched_reason=matched_reason,
            estimated_cost_usd=winner["cost_usd"],
            estimated_cost_inr=round(winner["cost_usd"] * 86.50, 4),
            estimated_latency_sec=winner["latency_sec"],
            expected_accuracy_percent=winner["accuracy_percent"],
            candidate_ranking=clean_ranking,
        )
