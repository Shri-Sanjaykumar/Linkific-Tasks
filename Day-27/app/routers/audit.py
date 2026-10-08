"""FastAPI REST API routes for FinDoc-AuditEngine."""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.models import InvoicePayload, PurchaseOrderRecord, AuditDecision
from app.services.matcher import ReconciliationMatcher
from app.services.anomaly_detector import AnomalyScorer
from app.services.router import ApprovalRouter
from app.core.privacy import FinancialPrivacyScrubber
from app.core.config import settings

router = APIRouter()

# In-memory PO database & Audit Ledger
PURCHASE_ORDERS: Dict[str, PurchaseOrderRecord] = {}
AUDIT_LEDGER: List[AuditDecision] = []

# Persistent ML model instance
anomaly_engine = AnomalyScorer()


from pydantic import BaseModel, Field, ConfigDict


class ProcessInvoiceRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    invoice: InvoicePayload
    associated_po: Optional[PurchaseOrderRecord] = Field(default=None, alias="purchase_order")


@router.post("/process", response_model=AuditDecision, status_code=status.HTTP_200_OK)
def process_financial_audit(req: ProcessInvoiceRequest):
    """End-to-End Financial Document Audit Endpoint.
    
    1. Pre-inference PII scrubbing
    2. Deterministic 3-way reconciliation
    3. Isolation Forest ML risk scoring
    4. Corporate governance tier routing (USD & INR)
    """
    invoice = req.invoice
    po = req.associated_po or PURCHASE_ORDERS.get(invoice.po_number or "")

    # 1. PII Scrubbing
    raw_blob = f"{invoice.vendor_contact_email or ''} {invoice.vendor_pan or ''} {invoice.vendor_bank_account or ''}"
    _, pii_count, _ = FinancialPrivacyScrubber.scrub_text(raw_blob)

    # 2. 3-Way Reconciliation
    match_result = ReconciliationMatcher.match(invoice, po)

    # 3. ML Risk & Anomaly Scoring
    risk_assessment = anomaly_engine.assess_risk(invoice, match_result)

    # 4. Multi-tier Governance Routing
    decision = ApprovalRouter.route_decision(
        invoice=invoice,
        match_res=match_result,
        risk=risk_assessment,
        pii_count=pii_count,
    )

    # Store in immutable audit ledger
    AUDIT_LEDGER.append(decision)

    return decision


@router.post("/po/register", status_code=status.HTTP_201_CREATED)
def register_purchase_order(po: PurchaseOrderRecord):
    """Register a commitment Purchase Order in the ERP ledger."""
    PURCHASE_ORDERS[po.po_number] = po
    return {"message": f"PO '{po.po_number}' registered successfully with {len(po.items)} line items."}


@router.get("/ledger", response_model=List[AuditDecision])
def get_audit_ledger():
    """Retrieve full audit history."""
    return AUDIT_LEDGER


@router.get("/summary")
def get_audit_summary():
    """Aggregated financial KPIs and governance statistics."""
    total_processed = len(AUDIT_LEDGER)
    total_authorized_usd = sum(d.total_amount_usd for d in AUDIT_LEDGER if d.authorized)
    total_authorized_inr = sum(d.total_amount_inr for d in AUDIT_LEDGER if d.authorized)
    stp_count = sum(1 for d in AUDIT_LEDGER if d.approval_tier.value == "TIER_1_STP_AUTO_APPROVED")

    return {
        "total_invoices_audited": total_processed,
        "total_disbursed_usd": round(total_authorized_usd, 2),
        "total_disbursed_inr": round(total_authorized_inr, 2),
        "stp_rate_percentage": round((stp_count / total_processed * 100.0) if total_processed > 0 else 0.0, 1),
        "exchange_rate_applied": settings.USD_TO_INR_RATE,
        "exchange_rate_usd_to_inr": settings.USD_TO_INR_RATE,
        "environment": settings.ENVIRONMENT,
    }
