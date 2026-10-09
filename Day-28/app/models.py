"""Enterprise Financial Pydantic v2 Data Models & Enums."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


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
    model_config = ConfigDict(extra="ignore")

    item_id: str
    description: str
    quantity: int = Field(..., ge=1, description="Quantity of units ordered/billed")
    unit_price_usd: float = Field(..., ge=0.0, description="Price per unit in USD")
    total_price_usd: float = Field(default=0.0, ge=0.0, description="Total price (quantity * unit_price)")

    @model_validator(mode="before")
    @classmethod
    def calculate_total_if_missing(cls, data: Any):
        if isinstance(data, dict):
            if (data.get("total_price_usd") is None or data.get("total_price_usd") == 0.0) and "quantity" in data and "unit_price_usd" in data:
                data["total_price_usd"] = round(float(data["quantity"]) * float(data["unit_price_usd"]), 2)
        return data


class InvoicePayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    invoice_id: str
    vendor_id: str = "VEND-DEFAULT"
    vendor_name: str
    po_number: Optional[str] = None
    invoice_date: str = "2026-10-01"
    due_date: str = "2026-10-31"
    subtotal_usd: float = Field(default=0.0, ge=0.0)
    tax_usd: float = Field(default=0.0, ge=0.0)
    total_amount_usd: float = Field(..., ge=0.0)
    currency: str = "USD"
    items: List[LineItem] = Field(default_factory=list)
    vendor_country: str = "IN"
    is_new_vendor: bool = False
    vendor_contact_email: Optional[str] = None
    vendor_pan: Optional[str] = None
    vendor_bank_account: Optional[str] = None


class PurchaseOrderRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    po_number: str
    vendor_id: str = "VEND-DEFAULT"
    vendor_name: Optional[str] = None
    approved_total_usd: float = Field(default=0.0, ge=0.0)
    items: List[LineItem] = Field(default_factory=list)
    grn_units_received: Dict[str, int] = Field(default_factory=dict)
    grn_units_rejected: Dict[str, int] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def resolve_amount_field(cls, data: Any):
        if isinstance(data, dict):
            if "total_amount_usd" in data and ("approved_total_usd" not in data or data["approved_total_usd"] == 0.0):
                data["approved_total_usd"] = data["total_amount_usd"]
        return data


class MatchResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    matched: bool
    po_found: bool
    price_variance_usd: float = 0.0
    quantity_variance_units: int = 0
    tax_variance_usd: float = 0.0
    discrepancy_details: List[str] = Field(default_factory=list)


class FeatureContribution(BaseModel):
    """Explainability vector element detailing how a single feature drove the risk score."""
    model_config = ConfigDict(extra="ignore")

    feature_name: str
    feature_value: str
    risk_contribution: float = Field(..., description="Calculated point contribution to 0-100 score")
    description: str


class RiskAssessment(BaseModel):
    model_config = ConfigDict(extra="ignore")

    anomaly_score: float = Field(..., ge=0.0, le=100.0)
    risk_level: RiskLevelEnum
    anomaly_detected: bool
    risk_factors: List[str] = Field(default_factory=list)
    feature_contributions: List[FeatureContribution] = Field(default_factory=list)


class AuditDecision(BaseModel):
    model_config = ConfigDict(extra="ignore")

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
    feature_contributions: List[FeatureContribution] = Field(default_factory=list)


class SystemErrorResponse(BaseModel):
    """Standardized RFC 7807 problem details error schema."""
    error_code: str
    message: str
    timestamp: str
    details: Dict[str, str] = Field(default_factory=dict)
