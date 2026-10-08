"""Pydantic v2 schemas for FinDoc-AuditEngine."""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field


class ApprovalTierEnum(str, Enum):
    TIER_1_STP = "TIER_1_STP_AUTO_APPROVED"
    TIER_2_MANAGER = "TIER_2_MANAGER_REVIEW"
    TIER_3_DIRECTOR = "TIER_3_DIRECTOR_SIGNOFF"
    REJECTED_DISCREPANCY = "REJECTED_DISCREPANCY"
    FROZEN_FRAUD_RISK = "FROZEN_FRAUD_RISK"


class RiskLevelEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class LineItem(BaseModel):
    item_id: str
    description: str
    quantity: int
    unit_price_usd: float
    total_price_usd: float


class InvoicePayload(BaseModel):
    invoice_id: str
    vendor_id: str
    vendor_name: str
    po_number: Optional[str] = None
    invoice_date: str
    due_date: str
    subtotal_usd: float
    tax_usd: float
    total_amount_usd: float
    currency: str = "USD"
    items: List[LineItem]
    vendor_country: str = "IN"
    is_new_vendor: bool = False
    vendor_contact_email: Optional[str] = None
    vendor_pan: Optional[str] = None
    vendor_bank_account: Optional[str] = None


class PurchaseOrderRecord(BaseModel):
    po_number: str
    vendor_id: str
    approved_total_usd: float
    items: List[LineItem]
    grn_units_received: Dict[str, int] = Field(default_factory=dict)
    grn_units_rejected: Dict[str, int] = Field(default_factory=dict)


class MatchResult(BaseModel):
    matched: bool
    po_found: bool
    price_variance_usd: float
    quantity_variance_units: int
    tax_variance_usd: float
    discrepancy_details: List[str] = Field(default_factory=list)


class RiskAssessment(BaseModel):
    anomaly_score: float = Field(..., description="ML isolation forest score mapped to 0-100")
    risk_level: RiskLevelEnum
    anomaly_detected: bool
    risk_factors: List[str] = Field(default_factory=list)


class AuditDecision(BaseModel):
    audit_id: str
    invoice_id: str
    timestamp: str
    approval_tier: ApprovalTierEnum
    authorized: bool
    total_amount_usd: float
    total_amount_inr: float
    variance_amount_usd: float
    variance_amount_inr: float
    risk_score: float
    risk_level: RiskLevelEnum
    requires_hitl: bool
    pii_redactions_made: int
    reconciliation_summary: str
    audit_flags: List[str] = Field(default_factory=list)
