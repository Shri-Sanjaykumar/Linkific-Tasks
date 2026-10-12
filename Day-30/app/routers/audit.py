"""Enterprise Financial Document Audit REST API Endpoints."""

import csv
import io
import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import APIRouter, Query, Response, status
from pydantic import BaseModel, ConfigDict, Field

from app.models import (
    InvoicePayload,
    PurchaseOrderRecord,
    AuditDecision,
    ApprovalTierEnum,
    LineItem,
    StageTimingTelemetry,
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


class RawDocumentParseRequest(BaseModel):
    raw_text: str


@router.post("/process", response_model=AuditDecision, status_code=status.HTTP_200_OK)
def process_financial_audit(req: ProcessInvoiceRequest):
    """End-to-End Dynamic Financial Document Audit Endpoint with Microsecond Telemetry."""
    t0 = time.perf_counter()
    invoice = req.invoice
    po = req.associated_po if req.associated_po is not None else PURCHASE_ORDERS.get(invoice.po_number or "")

    # 1. Pre-inference PII Scrubbing
    t_pii_start = time.perf_counter()
    raw_blob = f"{invoice.vendor_contact_email or ''} {invoice.vendor_pan or ''} {invoice.vendor_bank_account or ''}"
    _, pii_count, _ = FinancialPrivacyScrubber.scrub_text(raw_blob)
    pii_ms = round((time.perf_counter() - t_pii_start) * 1000.0, 3)

    # 2. Deterministic 3-Way Reconciliation
    t_rec_start = time.perf_counter()
    match_result = ReconciliationMatcher.match(invoice, po)
    rec_ms = round((time.perf_counter() - t_rec_start) * 1000.0, 3)

    # 3. Multivariate Isolation Forest ML Risk & Feature Attribution
    t_ml_start = time.perf_counter()
    risk_assessment = anomaly_engine.assess_risk(invoice, match_result)
    ml_ms = round((time.perf_counter() - t_ml_start) * 1000.0, 3)

    # 4. Multi-tier Corporate Governance Routing
    t_gov_start = time.perf_counter()
    total_ms = round((time.perf_counter() - t0) * 1000.0, 3)
    telemetry = StageTimingTelemetry(
        pii_scrub_ms=pii_ms,
        reconciliation_ms=rec_ms,
        ml_inference_ms=ml_ms,
        governance_routing_ms=round((time.perf_counter() - t_gov_start) * 1000.0, 3),
        total_pipeline_ms=total_ms,
    )

    decision = ApprovalRouter.route_decision(
        invoice=invoice,
        match_res=match_result,
        risk=risk_assessment,
        pii_count=pii_count,
        telemetry=telemetry,
    )

    AUDIT_LEDGER.insert(0, decision)
    return decision


@router.post("/parse-raw")
def parse_and_scrub_raw_document(req: RawDocumentParseRequest):
    """Dynamically parse unstructured invoice text, scrub PII tokens, and extract fields."""
    sanitized_text, pii_count, surrogates = FinancialPrivacyScrubber.scrub_text(req.raw_text)

    # Extract dynamic invoice attributes from free text if present
    inv_match = re.search(r"\b(?:INVOICE|INV)[-\s#:]+([A-Z0-9-]+)", req.raw_text, re.IGNORECASE)
    po_match = re.search(r"(?:PO)[-\s#:]*([A-Z0-9-]+)", req.raw_text, re.IGNORECASE)
    amt_match = re.search(r"\$\s*([0-9,]+(?:\.[0-9]{1,2})?)", req.raw_text)
    vendor_match = re.search(r"(?:Vendor|From|Supplier)[:\s]+([A-Za-z0-9\s.,&-]+?)(?:\n|$|;|,)", req.raw_text, re.IGNORECASE)
    country_match = re.search(r"(?:Country|Jurisdiction)[:\s]+([A-Z]{2})\b", req.raw_text, re.IGNORECASE)

    extracted_amount = float(amt_match.group(1).replace(",", "")) if amt_match else 1250.00
    email_found = next((v for k, v in surrogates.items() if "EMAIL" in k), "")
    pan_found = next((v for k, v in surrogates.items() if "PAN" in k), "")

    return {
        "sanitized_text": sanitized_text,
        "pii_redactions_count": pii_count,
        "surrogate_map": surrogates,
        "extracted_fields": {
            "invoice_id": f"INV-{inv_match.group(1)}" if inv_match and not inv_match.group(1).upper().startswith("INV") else (inv_match.group(1) if inv_match else "INV-PARSED-01"),
            "po_number": f"PO-{po_match.group(1)}" if po_match and not po_match.group(1).upper().startswith("PO") else (po_match.group(1) if po_match else "PO-9001"),
            "vendor_name": vendor_match.group(1).strip() if vendor_match else "Extracted Enterprise Vendor",
            "total_amount_usd": extracted_amount,
            "vendor_country": country_match.group(1).upper() if country_match else "IN",
            "vendor_contact_email": email_found,
            "vendor_pan": pan_found,
        },
    }


@router.post("/demo-batch", response_model=List[AuditDecision])
def run_mentor_demo_batch():
    """Execute all 5 enterprise benchmark scenarios in sequence for live mentor demonstrations."""
    presets = get_benchmark_presets()
    decisions: List[AuditDecision] = []
    for item in presets:
        inv = InvoicePayload(**item["invoice"])
        po = PurchaseOrderRecord(**item["po"]) if item.get("po") else None
        req = ProcessInvoiceRequest(invoice=inv, associated_po=po)
        decisions.append(process_financial_audit(req))
    return decisions


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
    search: Optional[str] = Query(None, description="Search by Invoice ID or Vendor"),
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
        results = [
            d for d in results
            if q in d.invoice_id.lower() or q in (d.vendor_name or "").lower() or q in d.audit_id.lower()
        ]

    return results


@router.delete("/ledger/clear")
def clear_audit_ledger():
    """Reset the in-memory audit ledger for a clean demonstration run."""
    count = len(AUDIT_LEDGER)
    AUDIT_LEDGER.clear()
    return {"message": f"Cleared {count} audit record(s) from ledger.", "remaining": 0}


@router.get("/export/csv")
def export_ledger_csv():
    """Export the in-memory prototype audit ledger as a downloadable CSV compliance report."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Audit_ID",
        "Timestamp_UTC",
        "Invoice_ID",
        "Vendor_Name",
        "Country",
        "PO_Number",
        "Total_USD",
        "Total_INR_86_50",
        "Price_Variance_USD",
        "Qty_Variance_Units",
        "ML_Risk_Score",
        "Risk_Level",
        "Governance_Tier",
        "Authorized",
        "PII_Redactions",
        "Summary",
    ])
    for d in AUDIT_LEDGER:
        writer.writerow([
            d.audit_id,
            d.timestamp,
            d.invoice_id,
            d.vendor_name,
            d.vendor_country,
            d.po_number or "N/A",
            f"{d.total_amount_usd:.2f}",
            f"{d.total_amount_inr:.2f}",
            f"{d.variance_amount_usd:.2f}",
            d.quantity_variance_units,
            f"{d.risk_score:.1f}",
            d.risk_level.value,
            d.approval_tier.value,
            "YES" if d.authorized else "NO",
            d.pii_redactions_made,
            d.reconciliation_summary,
        ])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=FinDoc_Audit_Compliance_Ledger.csv"},
    )


@router.get("/summary")
def get_audit_summary():
    """Aggregated financial KPIs and corporate governance portfolio statistics."""
    total_processed = len(AUDIT_LEDGER)
    total_authorized_usd = sum(d.total_amount_usd for d in AUDIT_LEDGER if d.authorized)
    total_authorized_inr = sum(d.total_amount_inr for d in AUDIT_LEDGER if d.authorized)
    blocked_usd = sum(d.total_amount_usd for d in AUDIT_LEDGER if not d.authorized)
    blocked_inr = sum(d.total_amount_inr for d in AUDIT_LEDGER if not d.authorized)
    stp_count = sum(1 for d in AUDIT_LEDGER if d.approval_tier == ApprovalTierEnum.TIER_1_STP)
    blocked_count = sum(1 for d in AUDIT_LEDGER if not d.authorized)
    avg_risk = round(sum(d.risk_score for d in AUDIT_LEDGER) / total_processed, 1) if total_processed > 0 else 0.0

    return {
        "total_invoices_audited": total_processed,
        "total_disbursed_usd": round(total_authorized_usd, 2),
        "total_disbursed_inr": round(total_authorized_inr, 2),
        "blocked_capital_usd": round(blocked_usd, 2),
        "blocked_capital_inr": round(blocked_inr, 2),
        "straight_through_processing_rate": f"{(stp_count / total_processed * 100.0) if total_processed > 0 else 0.0:.1f}%",
        "stp_rate_percentage": round((stp_count / total_processed * 100.0) if total_processed > 0 else 0.0, 1),
        "blocked_invoices_count": blocked_count,
        "average_risk_score": avg_risk,
        "exchange_rate_applied": settings.USD_TO_INR_RATE,
        "exchange_rate_usd_to_inr": settings.USD_TO_INR_RATE,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/presets")
def get_benchmark_presets():
    """Returns the 5 benchmark enterprise invoices for optional 1-click reference loading."""
    benchmark_file = Path(__file__).resolve().parent.parent.parent / "data" / "benchmark_invoices.json"
    if not benchmark_file.exists():
        benchmark_file = Path("data/benchmark_invoices.json")

    if benchmark_file.exists():
        with open(benchmark_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
