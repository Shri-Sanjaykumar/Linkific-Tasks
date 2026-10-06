"""Empirical Latency and Throughput Simulator based on published provider telemetry.

Calculates realistic TTFT (Time To First Token), token generation duration, and total latency
accounting for input context length and output token count.
"""

from typing import Dict, Any
from app.models import ModelSpec


class LatencySimulator:
    """Simulates realistic response times based on empirical TTFT and TPS metrics."""

    @staticmethod
    def calculate_expected_latency(
        model: ModelSpec,
        input_tokens: int,
        output_tokens: int,
        use_p95: bool = False,
    ) -> Dict[str, float]:
        """Compute end-to-end latency for a model call.
        
        End-to-End Latency = TTFT + (output_tokens / tokens_per_second)
        Also incorporates input prompt processing overhead (prefill delay).
        """
        # Base TTFT
        base_ttft = model.latency.p95_ttft_sec if use_p95 else model.latency.time_to_first_token_sec

        # Context prefill overhead: ~0.02s per 1k input tokens on standard GPUs, 0.005s on Groq LPUs
        if model.provider.value == "Groq":
            prefill_overhead = (input_tokens / 1000.0) * 0.005
        else:
            prefill_overhead = (input_tokens / 1000.0) * 0.015

        actual_ttft = base_ttft + prefill_overhead

        # Decode phase (generation)
        generation_time = output_tokens / model.latency.tokens_per_second if model.latency.tokens_per_second > 0 else 0.0

        total_latency = actual_ttft + generation_time

        return {
            "ttft_sec": round(actual_ttft, 3),
            "generation_time_sec": round(generation_time, 3),
            "total_latency_sec": round(total_latency, 3),
            "effective_tokens_per_second": round(output_tokens / total_latency, 1) if total_latency > 0 else 0.0,
        }
