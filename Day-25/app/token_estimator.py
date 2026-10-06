"""Token estimation and KV cache analysis utilities.

Uses deterministic character-to-token ratio (approximated for BPE cl100k / o200k / Claude / Gemini / Llama tokenizers)
and provides accurate token counts for prompt prefixes, systems prompts, and user inputs.
"""

import math
from typing import Dict, Any, Tuple


# Average ratio: ~3.75 - 4.0 characters per token for English text and structured JSON
CHARS_PER_TOKEN = 3.85


def estimate_tokens(text: str) -> int:
    """Estimate token count from raw text string."""
    if not text:
        return 0
    # Clean whitespace and calculate
    char_count = len(text)
    token_est = math.ceil(char_count / CHARS_PER_TOKEN)
    return max(1, token_est)


def calculate_cache_breakdown(
    system_prompt: str,
    few_shot_examples: str,
    user_payload: str,
    expected_output_tokens: int,
    cache_ttl_active: bool = True,
) -> Dict[str, Any]:
    """Calculate token breakdown separating static cacheable prefix from dynamic input tokens.
    
    In production architectures:
    - System instructions + Few-shot schemas remain static across all invoice runs.
    - User payload (current document) varies per invocation.
    """
    system_tokens = estimate_tokens(system_prompt)
    few_shot_tokens = estimate_tokens(few_shot_examples)
    dynamic_tokens = estimate_tokens(user_payload)
    
    static_prefix_tokens = system_tokens + few_shot_tokens
    total_input_tokens = static_prefix_tokens + dynamic_tokens
    
    cacheable_ratio = (static_prefix_tokens / total_input_tokens) if total_input_tokens > 0 else 0.0
    
    return {
        "system_tokens": system_tokens,
        "few_shot_tokens": few_shot_tokens,
        "dynamic_user_tokens": dynamic_tokens,
        "static_cacheable_prefix_tokens": static_prefix_tokens,
        "total_input_tokens": total_input_tokens,
        "expected_output_tokens": expected_output_tokens,
        "cacheable_ratio": round(cacheable_ratio, 4),
        "cache_eligible": static_prefix_tokens >= 1024 if cache_ttl_active else False,  # e.g., Anthropic min 1024 tokens for caching
    }
