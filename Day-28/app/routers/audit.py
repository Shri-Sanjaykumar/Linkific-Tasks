"""Enterprise Financial Document Audit REST API Endpoints."""

import json
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field

from app.models import (
    InvoicePayload,
    PurchaseOrderRecord,
    AuditDecision,
    ApprovalTierEnum,
)
from app.services.matcher import ReconciliationMatcher
from app.services.anomaly_detector import AnomalyScorer
from app.services.router import ApprovalRouter
from app.core.privacy import FinancialPrivacyScrubber
from app.core.config import settings
from app.core.logging_config import logger

router = APIRouter()

# In-memory PO database & Audit Ledger
PURCHASE_ORDERS: Dict[str, PurchaseOrderRecord] = {}
AUDIT_LEDGER: List[AuditDecision] = []

# Persistent ML model instance
anomaly_engine = AnomalyScorer()


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
    4. Corporate governance tier routing (USD & INR @ ₹86.50)
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

    # Store in immutable audit ledger (prepend to keep newest first)
    AUDIT_LEDGER.insert(0, decision)

    return decision


@router.post("/po/register", status_code=status.HTTP_201_CREATED)
def register_purchase_order(po: PurchaseOrderRecord):
    """Register a commitment Purchase Order in the ERP ledger."""
    PURCHASE_ORDERS[po.po_number] = po
    logger.info(f"ERP Ledger: Registered PO '{po.po_number}' with {len(po.items)} line items.")
    return {"message": f"PO '{po.po_number}' registered successfully with {len(po.items)} line items."}


@router.get("/ledger", response_model=List[AuditDecision])
def get_audit_ledger(
    tier: Optional[ApprovalTierEnum] = Query(None, description="Filter by approval tier"),
    min_amount: Optional[float] = Query(None, description="Minimum USD amount"),
    max_amount: Optional[float] = Query(None, description="Maximum USD amount"),
    search: Optional[str] = Query(None, description="Search by Invoice ID"),
):
    """Retrieve filterable audit ledger history."""
    results = AUDIT_LEDGER

    if tier:
        results = [d for d in results if d.approval_tier == tier]

    if min_amount is not None:
        results = [d for d in results if d.total_amount_usd >= min_amount]

    if max_amount is not None:
        results = [d for d in results if d.total_amount_usd <= max_amount]

    if search:
        q = search.lower()
        results = [d for d in results if q in d.invoice_id.lower()]

    return results


@router.get("/summary")
def get_audit_summary():
    """Aggregated financial KPIs and corporate governance portfolio statistics."""
    total_processed = len(AUDIT_LEDGER)
    total_authorized_usd = sum(d.total_amount_usd for d in AUDIT_LEDGER if d.authorized)
    total_authorized_inr = sum(d.total_amount_inr for d in AUDIT_LEDGER if d.authorized)
    stp_count = sum(1 for d in AUDIT_LEDGER if d.approval_tier == ApprovalTierEnum.TIER_1_STP)
    blocked_count = sum(1 for d in AUDIT_LEDGER if not d.authorized)

    return {
        "total_invoices_audited": total_processed,
        "total_disbursed_usd": round(total_authorized_usd, 2),
        "total_disbursed_inr": round(total_authorized_inr, 2),
        "straight_through_processing_rate": f"{(stp_count / total_processed * 100.0) if total_processed > 0 else 0.0:.1f}%",
        "stp_rate_percentage": round((stp_count / total_processed * 100.0) if total_processed > 0 else 0.0, 1),
        "blocked_invoices_count": blocked_count,
        "exchange_rate_applied": settings.USD_TO_INR_RATE,
        "exchange_rate_usd_to_inr": settings.USD_TO_INR_RATE,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/presets")
def get_benchmark_presets():
    """Returns the 5 benchmark enterprise invoices for 1-click UI pre-population."""
    benchmark_file = Path(__file__).resolve().parent.parent.parent / "data" / "benchmark_invoices.json"
    if not benchmark_file.exists():
        # Fallback path
        benchmark_file = Path("data/benchmark_invoices.json")

    if benchmark_file.exists():
        with open(benchmark_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
