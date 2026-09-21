"""
Utility helpers for query preprocessing, text cleaning, and logging.
"""

import re
from typing import List

STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "so", "of", "to", "in",
    "on", "at", "for", "with", "about", "is", "are", "was", "were", "be", "been",
    "can", "could", "would", "should", "what", "which", "who", "whom", "this",
    "that", "these", "those", "how", "why", "where", "when", "tell", "me", "please",
    "i", "want", "know", "need", "give", "explain"
}

def clean_text(text: str) -> str:
    """Normalize whitespace and strip unprintable characters."""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def extract_keywords(query: str) -> List[str]:
    """Extract substantive keywords from query, filtering common stop words."""
    tokens = re.findall(r"\b[a-zA-Z0-9_-]{2,}\b", query.lower())
    keywords = [t for t in tokens if t not in STOP_WORDS]
    return keywords

def format_trace(trace: List[str]) -> str:
    """Format execution trace as a readable markdown list."""
    return "\n".join(f"{i+1}. {step}" for i, step in enumerate(trace))
