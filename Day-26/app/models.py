"""Pydantic data models for Responsible AI Guardrail POC."""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field


class PIITypeEnum(str, Enum):
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    CREDIT_CARD = "CREDIT_CARD"
    SSN = "SSN"
    AADHAAR = "AADHAAR"
    PAN = "PAN"
    ACCOUNT_NUMBER = "ACCOUNT_NUMBER"


class MaskedToken(BaseModel):
    original_text: str
    token_type: PIITypeEnum
    surrogate: str
    start_pos: int
    end_pos: int


class PrivacyScrubResult(BaseModel):
    original_text: str
    sanitized_text: str
    redacted_count: int
    masked_tokens: List[MaskedToken]
    surrogate_map: Dict[str, str] = Field(default_factory=dict)


class FairnessMetrics(BaseModel):
    total_evaluated: int
    group_a_name: str
    group_b_name: str
    group_a_approval_rate: float
    group_b_approval_rate: float
    disparate_impact_ratio: float
    demographic_parity_difference: float
    equal_opportunity_difference: Optional[float] = None
    passes_four_fifths_rule: bool
    status: str
    violations: List[str] = Field(default_factory=list)


class GroundingVerificationResult(BaseModel):
    is_grounded: bool
    citation_coverage_score: float
    unsupported_claims: List[str] = Field(default_factory=list)
    numerical_discrepancies: List[Dict[str, Any]] = Field(default_factory=list)
    status: str
    action: str  # "ALLOW", "FLAG_WARNING", "BLOCK_HALLUCINATION"


class GuardrailAuditRecord(BaseModel):
    record_id: str
    timestamp: str
    privacy_passed: bool
    privacy_redactions_made: int
    grounding_passed: bool
    citation_score: float
    fairness_passed: bool
    disparate_impact_ratio: float
    overall_compliance_decision: str  # "APPROVED", "REJECTED_ETHICS_VIOLATION"
    violations_summary: List[str] = Field(default_factory=list)
