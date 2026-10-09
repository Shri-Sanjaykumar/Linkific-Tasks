"""CLI Execution and Benchmark Demonstration Runner for FinDoc-AuditEngine (Day 28).

Demonstrates the refactored, production-hardened FinDoc-AuditEngine:
- Pre-inference PII scrubbing
- Deterministic 3-way matching (Invoice vs PO vs GRN dock receipt)
- Unsupervised Isolation Forest ML Risk & Anomaly Scoring with explainable feature contributions
- Multi-tier corporate governance routing with dual currency pegging (USD & INR @ ₹86.50)
- Real-time financial portfolio KPIs
"""

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from app.core.config import settings
from app.models import InvoicePayload, PurchaseOrderRecord
from app.routers.audit import (
    ProcessInvoiceRequest,
    get_audit_summary,
    process_financial_audit,
)


def print_banner():
    banner = f"""
========================================================================================================
     LINKIFIC ENTERPRISE AI AUDIT GATEWAY — DAY 28 FEATURE INTEGRATION & CODE REVIEW
     Service: FinDoc-AuditEngine v{settings.APP_VERSION} (Reconciliation + ML Risk + Dual Currency + Portal)
     Fixed Corporate FX Peg: 1 USD = INR {settings.USD_TO_INR_RATE:.2f}
========================================================================================================
"""
    print(banner)


def run_benchmark_demo():
    """Execute evaluation cases from benchmark_invoices.json and display structured audit tables."""
    data_path = os.path.join(BASE_DIR, "data", "benchmark_invoices.json")
    with open(data_path, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    print(f"\n[1] AUDITING BATCH OF {len(test_cases)} REAL-WORLD ENTERPRISE FINANCIAL INVOICES:")
    print("-" * 140)
    print(
        f"{'Invoice ID':<10} | {'Vendor Name':<28} | {'Amount (USD)':<13} | "
        f"{'Amount (INR)':<18} | {'Risk':<6} | {'Tier Decision':<26} | {'Action':<10}"
    )
    print("-" * 140)

    for tc in test_cases:
        inv = InvoicePayload(**tc["invoice"])
        po = PurchaseOrderRecord(**tc["po"]) if tc.get("po") else None

        req = ProcessInvoiceRequest(invoice=inv, associated_po=po)
        decision = process_financial_audit(req)

        status_str = "APPROVED" if decision.authorized else "BLOCKED"
        print(
            f"{decision.invoice_id:<10} | "
            f"{inv.vendor_name[:26]:<28} | "
            f"${decision.total_amount_usd:<12,.2f} | "
            f"INR {decision.total_amount_inr:<14,.2f} | "
            f"{decision.risk_score:<6.1f} | "
            f"{decision.approval_tier.value:<26} | "
            f"{status_str:<10}"
        )

        # Print reasoning and top explainable ML factor
        print(f"   ↳ Governance: {decision.reconciliation_summary}")
        if decision.audit_flags:
            print(f"   ↳ Risk Signals: {', '.join(decision.audit_flags)}")
        print()

    print("-" * 140)

    # Print Summary KPI
    summary = get_audit_summary()
    print("\n[2] REAL-TIME AGGREGATE FINANCIAL PORTFOLIO & AUDIT METRICS:")
    print(f"  - Total Invoices Audited        : {summary['total_invoices_audited']}")
    print(f"  - Total Disbursed Capital (USD) : ${summary['total_disbursed_usd']:,.2f}")
    print(f"  - Total Disbursed Capital (INR) : INR {summary['total_disbursed_inr']:,.2f}")
    print(f"  - Straight-Through Rate (STP)   : {summary['stp_rate_percentage']:.1f}%")
    print(f"  - Blocked / High-Risk Invoices  : {summary['blocked_invoices_count']}")
    print(f"  - Corporate Exchange Rate       : 1 USD = INR {summary['exchange_rate_applied']:.2f}")
    print("=" * 140 + "\n")


def main():
    print_banner()
    run_benchmark_demo()


if __name__ == "__main__":
    main()
