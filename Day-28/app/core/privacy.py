"""Responsible AI PII Scrubber and Numerical Verifier for FinDoc-AuditEngine."""

import re
from typing import Dict, List, Tuple
from app.core.logging_config import logger


class FinancialPrivacyScrubber:
    """Detects and masks sensitive PII on financial payloads before storage or external transmission."""

    # Pre-compiled regex patterns for maximum efficiency
    PATTERNS: List[Tuple[str, re.Pattern, str]] = [
        ("EMAIL", re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}\b'), "[EMAIL_MASKED]"),
        ("PAN", re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'), "[PAN_MASKED]"),
        ("CREDIT_CARD", re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'), "[CREDIT_CARD_MASKED]"),
        ("ACCOUNT", re.compile(r'(?i)(?:account|acct|iban|acc)[:\s#]*([0-9]{8,18})\b'), "[ACCOUNT_MASKED]"),
        ("PHONE", re.compile(r'(?:\+91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}\b'), "[PHONE_MASKED]"),
        ("AADHAAR", re.compile(r'\b[1-9]\d{3}\s?\d{4}\s?\d{4}\b'), "[AADHAAR_MASKED]"),
    ]

    @classmethod
    def scrub_text(cls, text: str) -> Tuple[str, int, Dict[str, str]]:
        """Sanitize raw text string, returning masked string, redactions count, and surrogate map."""
        if not text:
            return "", 0, {}

        sanitized = text
        redacted_count = 0
        surrogates: Dict[str, str] = {}

        for name, regex, _ in cls.PATTERNS:
            for match in regex.finditer(text):
                val = match.group(0)
                if name == "ACCOUNT" and match.groups():
                    val = match.group(1)

                redacted_count += 1
                surrogate = f"[{name}_{redacted_count:02d}]"
                surrogates[surrogate] = val
                sanitized = sanitized.replace(val, surrogate)

        if redacted_count > 0:
            logger.info(f"Privacy Gate: Sanitized {redacted_count} PII token(s) from financial text.")

        return sanitized, redacted_count, surrogates

    @classmethod
    def scrub_invoice(cls, invoice: "InvoicePayload") -> Tuple["InvoicePayload", int]:
        """Sanitize an InvoicePayload object, masking PAN, email, account, etc."""
        inv_dict = invoice.model_dump()
        redacted_count = 0

        if inv_dict.get("vendor_pan"):
            inv_dict["vendor_pan"] = "[REDACTED_PAN]"
            redacted_count += 1

        if inv_dict.get("vendor_contact_email"):
            inv_dict["vendor_contact_email"] = "[REDACTED_EMAIL]"
            redacted_count += 1

        if inv_dict.get("vendor_bank_account"):
            inv_dict["vendor_bank_account"] = "[REDACTED_ACCOUNT]"
            redacted_count += 1

        from app.models import InvoicePayload
        return InvoicePayload(**inv_dict), redacted_count


PIIScrubber = FinancialPrivacyScrubber
