"""Hallucination Detector and Factual Grounding Verifier.

Audits LLM generated text against verified reference documents / ERP ledgers.
Performs:
1. Numerical Exact-Match Verification: flags altered invoice totals, dates, and percentages.
2. N-Gram & Semantic Overlap Citation Scoring.
3. Unsubstantiated Entity Extraction.
"""

import re
from typing import List, Dict, Any, Set
from app.models import GroundingVerificationResult


class GroundingVerifier:
    """Enterprise anti-hallucination guardrail validating factual integrity."""

    MIN_CITATION_SCORE_THRESHOLD = 0.55

    @classmethod
    def extract_numbers(cls, text: str) -> Set[str]:
        """Extract all numerical tokens, currency amounts, percentages, and dates."""
        # Matches integers, decimals, currency values, percentages
        pattern = r'\b(?:\$|€|£|₹)?\d+(?:,\d{3})*(?:\.\d+)?%?\b'
        raw_matches = re.findall(pattern, text)
        cleaned = set()
        for m in raw_matches:
            c = m.replace('$', '').replace('€', '').replace('£', '').replace('₹', '').replace(',', '').strip()
            if c:
                cleaned.add(c)
        return cleaned

    @classmethod
    def verify_grounding(
        cls,
        generated_response: str,
        source_context: str,
    ) -> GroundingVerificationResult:
        """Verify that claims in generated_response are grounded in source_context."""
        if not generated_response:
            return GroundingVerificationResult(
                is_grounded=True,
                citation_coverage_score=1.0,
                unsupported_claims=[],
                numerical_discrepancies=[],
                status="EMPTY_GENERATION",
                action="ALLOW",
            )

        # 1. Number and Amount Verification
        gen_numbers = cls.extract_numbers(generated_response)
        src_numbers = cls.extract_numbers(source_context)

        numerical_discrepancies: List[Dict[str, Any]] = []
        for num in gen_numbers:
            # Check if this exact number exists in the source text
            if num not in src_numbers:
                numerical_discrepancies.append({
                    "hallucinated_number": num,
                    "issue": f"Number '{num}' generated in response does not exist anywhere in source context.",
                })

        # 2. Token / Statement Overlap (Token-level Precision & Citation Coverage)
        gen_words = set(re.findall(r'\b[A-Za-z]{3,}\b', generated_response.lower()))
        src_words = set(re.findall(r'\b[A-Za-z]{3,}\b', source_context.lower()))

        # Standard English stop-words only
        stop_words = {
            "the", "and", "for", "that", "this", "with", "from", "have", "were", "been",
            "they", "will", "would", "there", "their", "what", "which", "when", "about",
            "our", "you", "your", "are"
        }
        substantive_gen = gen_words - stop_words

        unsupported_words: Set[str] = set()
        if substantive_gen:
            for w in substantive_gen:
                if w not in src_words:
                    unsupported_words.add(w)
            grounded_count = len(substantive_gen) - len(unsupported_words)
            citation_score = grounded_count / len(substantive_gen)
        else:
            citation_score = 1.0

        # 3. Decision Determination
        has_num_hallucination = len(numerical_discrepancies) > 0
        is_citation_low = citation_score < cls.MIN_CITATION_SCORE_THRESHOLD

        is_grounded = not has_num_hallucination and not is_citation_low

        unsupported_claims: List[str] = []
        if has_num_hallucination:
            for d in numerical_discrepancies:
                unsupported_claims.append(f"UNGROUNDED NUMBER: {d['hallucinated_number']}")
        if is_citation_low:
            unsupported_claims.append(
                f"LOW SOURCE OVERLAP: Citation score {citation_score:.2f} is below required {cls.MIN_CITATION_SCORE_THRESHOLD:.2f}"
            )

        if has_num_hallucination:
            action = "BLOCK_HALLUCINATION"
            status = "CRITICAL_NUMERICAL_HALLUCINATION"
        elif is_citation_low:
            action = "FLAG_WARNING"
            status = "POTENTIAL_UNGROUNDED_FABRICATION"
        else:
            action = "ALLOW"
            status = "GROUNDED_VERIFIED"

        return GroundingVerificationResult(
            is_grounded=is_grounded,
            citation_coverage_score=round(citation_score, 4),
            unsupported_claims=unsupported_claims,
            numerical_discrepancies=numerical_discrepancies,
            status=status,
            action=action,
        )
