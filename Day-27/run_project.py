"""CLI Execution and Benchmark Demonstration Runner for FinDoc-AuditEngine."""

import os
import sys
import json
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.models import InvoicePayload, PurchaseOrderRecord
from app.routers.audit import ProcessInvoiceRequest, process_financial_audit, get_audit_summary
from app.core.config import settings


def print_banner():
    banner = f"""
====================================================================================================
     LINKIFIC ENTERPRISE AI AUDIT GATEWAY - DAY 27 PROJECT PRACTICAL
     Service: FinDoc-AuditEngine (3-Way Matching + ML Anomaly Detection + Multi-Tier HITL)
     Baseline Currency Conversion: 1 USD = INR {settings.USD_TO_INR_RATE:.2f}
====================================================================================================
"""
    print(banner)


def run_benchmark_demo():
    """Execute evaluation cases from benchmark_invoices.json and display structured audit tables."""
    data_path = os.path.join(BASE_DIR, "data", "benchmark_invoices.json")
    with open(data_path, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    print(f"\n[1] PROCESSING BATCH OF {len(test_cases)} REAL-WORLD ENTERPRISE FINANCIAL INVOICES:")
    print("-" * 135)
    print(f"{'Invoice ID':<10} | {'Vendor Name':<28} | {'Amount (USD)':<14} | {'Amount (INR)':<18} | {'Risk':<6} | {'Tier Decision':<26} | {'Status':<10}")
    print("-" * 135)

    for tc in test_cases:
        inv = InvoicePayload(**tc["invoice"])
        po = PurchaseOrderRecord(**tc["po"]) if tc.get("po") else None

        req = ProcessInvoiceRequest(invoice=inv, associated_po=po)
        decision = process_financial_audit(req)

        status_str = "APPROVED" if decision.authorized else "BLOCKED"
        print(
            f"{decision.invoice_id:<10} | "
            f"{inv.vendor_name[:26]:<28} | "
            f"${decision.total_amount_usd:<13,.2f} | "
            f"INR {decision.total_amount_inr:<14,.2f} | "
            f"{decision.risk_score:<6.1f} | "
            f"{decision.approval_tier.value:<26} | "
            f"{status_str:<10}"
        )

    print("-" * 135)

    # Print Summary KPI
    summary = get_audit_summary()
    print("\n[2] AGGREGATE FINANCIAL PORTFOLIO & AUDIT METRICS:")
    print(f"  - Total Invoices Processed     : {summary['total_invoices_audited']}")
    print(f"  - Total Disbursed Capital (USD): ${summary['total_disbursed_usd']:,.2f}")
    print(f"  - Total Disbursed Capital (INR): INR {summary['total_disbursed_inr']:,.2f}")
    print(f"  - Straight-Through Rate (STP)  : {summary['stp_rate_percentage']:.1f}%")
    print(f"  - Exchange Rate Applied        : 1 USD = INR {summary['exchange_rate_applied']:.2f}")
    print("=" * 135 + "\n")


def main():
    print_banner()
    run_benchmark_demo()


if __name__ == "__main__":
    main()
