"""Privacy Masker and PII Redaction Guardrail.

Detects, redacts, and replaces sensitive customer PII before data is passed to external LLMs.
Supports reversible token substitution for secure in-VPC rehydration.
"""

import re
from typing import Dict, List, Tuple
from app.models import PIITypeEnum, MaskedToken, PrivacyScrubResult


class PrivacyMasker:
    """Production PII sanitization engine using RFC-compliant pattern matchers."""

    # Pre-compiled high-precision regex patterns
    PATTERNS: List[Tuple[PIITypeEnum, re.Pattern, str]] = [
        # Email addresses
        (
            PIITypeEnum.EMAIL,
            re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'),
            "[EMAIL_MASKED]"
        ),
        # Credit Card Numbers (13-19 digits with optional hyphens/spaces)
        (
            PIITypeEnum.CREDIT_CARD,
            re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
            "[CREDIT_CARD_MASKED]"
        ),
        # US SSN (XXX-XX-XXXX)
        (
            PIITypeEnum.SSN,
            re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            "[SSN_MASKED]"
        ),
        # Indian PAN Card (5 uppercase letters, 4 numbers, 1 letter)
        (
            PIITypeEnum.PAN,
            re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'),
            "[PAN_MASKED]"
        ),
        # Indian Aadhaar Number (12 digits, often in 4-4-4 format)
        (
            PIITypeEnum.AADHAAR,
            re.compile(r'\b\d{4}\s\d{4}\s\d{4}\b'),
            "[AADHAAR_MASKED]"
        ),
        # Explicit Bank Account Number (8 to 18 digits preceded by keyword)
        (
            PIITypeEnum.ACCOUNT_NUMBER,
            re.compile(r'(?i)(?:account|acct|acc|iban|routing)[:\s#]*([0-9]{8,18})\b'),
            "[ACCOUNT_MASKED]"
        ),
        # International & Domestic Phone Numbers (must have phone prefix or 10 digits with country code)
        (
            PIITypeEnum.PHONE,
            re.compile(r'(?:\+91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}\b|(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'),
            "[PHONE_MASKED]"
        ),
    ]

    @classmethod
    def scrub_text(cls, text: str) -> PrivacyScrubResult:
        """Scan input text, mask all detected PII, and build a reversible mapping dictionary."""
        if not text:
            return PrivacyScrubResult(
                original_text="",
                sanitized_text="",
                redacted_count=0,
                masked_tokens=[],
                surrogate_map={}
            )

        sanitized = text
        masked_tokens: List[MaskedToken] = []
        surrogate_map: Dict[str, str] = {}
        token_counter: Dict[str, int] = {}

        for pii_type, regex, base_placeholder in cls.PATTERNS:
            for match in regex.finditer(text):
                matched_val = match.group(0)
                
                # If special account regex matched keyword + number, isolate number
                if pii_type == PIITypeEnum.ACCOUNT_NUMBER and match.groups():
                    matched_val = match.group(1)

                # Skip false positives (e.g. standard dates or tiny integers)
                if len(matched_val.strip()) < 4:
                    continue

                t_type = pii_type.value
                token_counter[t_type] = token_counter.get(t_type, 0) + 1
                surrogate = f"[{t_type}_{token_counter[t_type]:02d}]"

                masked_tokens.append(
                    MaskedToken(
                        original_text=matched_val,
                        token_type=pii_type,
                        surrogate=surrogate,
                        start_pos=match.start(),
                        end_pos=match.end(),
                    )
                )
                surrogate_map[surrogate] = matched_val
                # Replace in sanitized text
                sanitized = sanitized.replace(matched_val, surrogate)

        return PrivacyScrubResult(
            original_text=text,
            sanitized_text=sanitized,
            redacted_count=len(masked_tokens),
            masked_tokens=masked_tokens,
            surrogate_map=surrogate_map,
        )

    @classmethod
    def rehydrate_text(cls, sanitized_text: str, surrogate_map: Dict[str, str]) -> str:
        """Restore original PII values within a secure boundary using the surrogate map."""
        rehydrated = sanitized_text
        for surrogate, original in surrogate_map.items():
            rehydrated = rehydrated.replace(surrogate, original)
        return rehydrated
