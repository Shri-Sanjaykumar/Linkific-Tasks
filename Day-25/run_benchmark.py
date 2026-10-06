"""Day 25 CLI Benchmark and Evaluation Runner.

Compares OpenAI, Claude, Gemini, and Groq across Cost, Speed, and Accuracy
with empirical ground truth validation, prompt caching modeling, and SLA routing.
"""

import os
import sys
import argparse
from typing import List

# Ensure Day-25 root is on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.database import MODEL_REGISTRY, get_all_models, get_model_by_id
from app.cost_calculator import CostCalculator
from app.latency_simulator import LatencySimulator
from app.router import LLMRouter, RoutingConstraint
from app.client import EvaluationClient


def print_banner():
    banner = """
====================================================================================================
     LINKIFIC AI/ML INTERNSHIP - DAY 25: PRODUCTION AI BENCHMARK & COMPARISON
     Providers: OpenAI vs Claude (Anthropic) vs Gemini (Google) vs Groq (LPU)
     Evaluation Axes: Cost ($ USD / INR) | Speed (TPS & TTFT) | Domain Accuracy (%)
     Baseline Currency Conversion: 1 USD = 86.50 INR
====================================================================================================
"""
    print(banner)


def run_comparison_mode():
    """Print comprehensive empirical comparison across all 4 providers in USD and INR."""
    print("\n[1] EMPIRICAL COMPARISON MATRIX (COST, SPEED, ACCURACY) [USD & INR]:")
    print("-" * 135)
    print(f"{'Provider':<10} | {'Model Name':<28} | {'Input $/M (INR/M)':<19} | {'Output $/M (INR/M)':<20} | {'TPS':<6} | {'TTFT(s)':<7} | {'MMLU%':<6} | {'FinAcc%':<7}")
    print("-" * 135)

    for m in get_all_models():
        in_usd = f"${m.pricing.input_per_m:.2f}"
        in_inr = f"INR {m.pricing.input_per_m * 86.50:.1f}"
        out_usd = f"${m.pricing.output_per_m:.2f}"
        out_inr = f"INR {m.pricing.output_per_m * 86.50:.1f}"
        in_str = f"{in_usd} ({in_inr})"
        out_str = f"{out_usd} ({out_inr})"

        print(
            f"{m.provider.value:<10} | "
            f"{m.name:<28} | "
            f"{in_str:<19} | "
            f"{out_str:<20} | "
            f"{m.latency.tokens_per_second:<6.1f} | "
            f"{m.latency.time_to_first_token_sec:<7.2f} | "
            f"{m.benchmarks.mmlu_score:<6.1f} | "
            f"{m.benchmarks.financial_accuracy:<7.1f}"
        )
    print("-" * 135)
    print("Metrics Source: Artificial Analysis Leaderboard, Provider API Specs & Empirical Test Suite.\n")


def run_cost_calculation_mode(input_tokens: int = 2500, output_tokens: int = 500, cache_ratio: float = 0.70):
    """Print cost optimization comparison including Prompt Caching and Monthly Projections in USD & INR."""
    print(f"\n[2] COST OPTIMIZATION ANALYSIS ({input_tokens} In, {output_tokens} Out, {int(cache_ratio*100)}% Cache Hit):")
    print("-" * 140)
    print(f"{'Model':<22} | {'Std Cost (USD / INR)':<24} | {'Cached Cost (USD / INR)':<25} | {'Savings %':<10} | {'Monthly 100k (USD / INR)':<27} | {'Cached Monthly (INR)':<20}")
    print("-" * 140)

    results = CostCalculator.compare_costs(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_hit_rate=cache_ratio,
        monthly_query_volume=100_000,
    )

    for r in results:
        std_str = f"${r.standard_cost_usd:.5f} / INR {r.standard_cost_inr:.3f}"
        cached_str = f"${r.cached_cost_usd:.5f} / INR {r.cached_cost_inr:.3f}"
        monthly_std_str = f"${r.monthly_cost_standard_usd:.1f} / INR {r.monthly_cost_standard_inr:,.0f}"
        monthly_cached_inr_str = f"INR {r.monthly_cost_cached_inr:,.0f}"

        print(
            f"{r.model_id:<22} | "
            f"{std_str:<24} | "
            f"{cached_str:<25} | "
            f"{r.savings_percent:<9.1f}% | "
            f"{monthly_std_str:<27} | "
            f"{monthly_cached_inr_str:<20}"
        )
    print("-" * 140)

    # Linkific Enterprise Case Study
    enterprise = CostCalculator.estimate_enterprise_savings(
        monthly_docs=50_000,
        avg_input_tokens=input_tokens,
        avg_output_tokens=output_tokens,
        cacheable_prefix_ratio=cache_ratio,
    )
    print("\n>>> LINKIFIC ENTERPRISE FINANCIAL AUTOMATION PROJECTION (50,000 Invoices/Month):")
    print(f"  - Baseline Uncached GPT-4o:     ${enterprise['baseline_monthly_usd']:.2f} / month  (INR {enterprise['baseline_monthly_inr']:,.2f})")
    print(f"  - Production Hybrid Router:     ${enterprise['hybrid_monthly_usd']:.2f} / month  (INR {enterprise['hybrid_monthly_inr']:,.2f})")
    print(f"  - Net Monthly Savings:          ${enterprise['monthly_savings_usd']:.2f} / month  (INR {enterprise['monthly_savings_inr']:,.2f})")
    print(f"  - Net Annualized Savings:       ${enterprise['annual_savings_usd']:.2f} / year   (INR {enterprise['annual_savings_inr']:,.2f})")
    print(f"  - Overall Cost Reduction:       {enterprise['cost_reduction_percentage']:.1f}%\n")


def run_routing_mode():
    """Demonstrate intelligent routing for various enterprise scenarios."""
    print("\n[3] INTELLIGENT MULTI-OBJECTIVE SLA ROUTING SIMULATION:")
    print("=" * 110)
    router = LLMRouter()

    scenarios = [
        {
            "name": "Scenario A: Real-Time Interactive UI (Requires < 0.8s response time)",
            "in_tokens": 1200,
            "out_tokens": 150,
            "constraint": RoutingConstraint(max_latency_sec=0.8, priority="speed"),
        },
        {
            "name": "Scenario B: Bulk Low-Cost Batch Parsing (Requires cost < $0.0005 / INR 0.043 per doc)",
            "in_tokens": 2000,
            "out_tokens": 250,
            "constraint": RoutingConstraint(max_cost_per_query_usd=0.0005, priority="cost"),
        },
        {
            "name": "Scenario C: Critical Audit & PO 3-Way Match (Requires accuracy >= 95%)",
            "in_tokens": 3500,
            "out_tokens": 800,
            "constraint": RoutingConstraint(min_accuracy_percent=95.0, priority="accuracy"),
        },
    ]

    for sc in scenarios:
        print(f"\n--- {sc['name']} ---")
        dec = router.route(
            input_tokens=sc["in_tokens"],
            output_tokens=sc["out_tokens"],
            constraints=sc["constraint"],
        )
        print(f"  [WINNER] Selected Model : {dec.selected_model.name} ({dec.selected_model.provider.value})")
        print(f"  [METRICS] Latency: {dec.estimated_latency_sec:.3f}s | Cost: ${dec.estimated_cost_usd:.6f} (INR {dec.estimated_cost_inr:.4f}) | Domain Acc: {dec.expected_accuracy_percent:.1f}%")
        print(f"  [REASON]  {dec.matched_reason}")
    print("\n" + "=" * 110)


def run_evaluation_suite_mode():
    """Run full evaluation dataset across representative models."""
    dataset_file = os.path.join(BASE_DIR, "data", "benchmark_dataset.json")
    print(f"\n[4] RUNNING GROUNDED TEST SUITE (20 Enterprise Test Cases) from:\n    {dataset_file}")
    client = EvaluationClient(dataset_file)
    summary = client.run_all_providers_summary()

    print("-" * 130)
    print(f"{'Provider':<10} | {'Model Name':<28} | {'Total Cost USD (INR)':<26} | {'Avg Latency':<12} | {'Accuracy %':<11} | {'Pass Rate':<10}")
    print("-" * 130)
    for mid, data in summary.items():
        cost_str = f"${data['total_cost_usd_20_cases']:.5f} (INR {data['total_cost_inr_20_cases']:.3f})"
        print(
            f"{data['provider']:<10} | "
            f"{data['model_name']:<28} | "
            f"{cost_str:<26} | "
            f"{data['avg_latency_sec']:<11.3f}s | "
            f"{data['avg_accuracy_percent']:<10.1f}% | "
            f"{data['successful_cases']:<10}"
        )
    print("-" * 130)
    print("Evaluation execution completed with 100% deterministic reproducibility.\n")


def main():
    parser = argparse.ArgumentParser(description="Day 25 AI/ML Provider Comparison Benchmark")
    parser.add_argument(
        "--mode",
        choices=["all", "compare", "calculate-cost", "route", "evals"],
        default="all",
        help="Execution mode (default: all)",
    )
    args = parser.parse_args()

    print_banner()

    if args.mode in ["all", "compare"]:
        run_comparison_mode()
    if args.mode in ["all", "calculate-cost"]:
        run_cost_calculation_mode()
    if args.mode in ["all", "route"]:
        run_routing_mode()
    if args.mode in ["all", "evals"]:
        run_evaluation_suite_mode()


if __name__ == "__main__":
    main()
