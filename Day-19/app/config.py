"""
Configuration settings, thresholds, and constants for Day 19 LangGraph workflow.
"""

import os
from typing import Dict, Any

class WorkflowConfig:
    # Directory paths
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    
    # Retrieval & embedding settings
    EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION = 384
    DEFAULT_TOP_K = 3
    
    # Heuristic similarity threshold in range [0.0, 1.0] (Cosine Similarity)
    # Higher values indicate greater semantic proximity.
    SIMILARITY_THRESHOLD = 0.45
    
    # Retry limits
    # max_retries counts additional retrieval attempts after the initial retrieval.
    # Initial attempt = 1, Retry 1 = 2, Retry 2 = 3. Maximum total attempts = 3.
    MAX_RETRIES = 2
    
    # Minimum question length (characters) to prevent whitespace or single-letter input
    MIN_QUESTION_LENGTH = 3
    
    # Safe fallback messages
    FALLBACK_NO_CONTEXT = (
        "I could not find enough relevant information in the available documentation "
        "to answer this question reliably. Please try rephrasing your question or "
        "refer to the employee handbook."
    )
    FALLBACK_EMPTY_INPUT = (
        "Invalid input: Please provide a valid, non-empty question with at least 3 characters."
    )
    FALLBACK_RETRIEVAL_ERROR = (
        "A temporary retrieval service error occurred while searching the documentation. "
        "Please try again or contact IT support if the issue persists."
    )
    FALLBACK_GENERATION_ERROR = (
        "An unexpected error occurred during answer synthesis. "
        "Please try rephrasing your query."
    )
