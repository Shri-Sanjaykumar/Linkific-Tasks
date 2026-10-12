"""Interactive 5-Stage Live Mentor Demonstration Script for Day 29.

Walks mentors through:
Stage 1: System Health & 7D ML Readiness Telemetry
Stage 2: Live Free-Text Invoice Parsing & Pre-Inference PII Scrubbing
Stage 3: Dynamic Multi-Line Custom Invoice Evaluation (Rate Markup + Dock Damage)
Stage 4: Full 5-Scenario Enterprise Benchmark Batch Execution
Stage 5: CSV Compliance Ledger Export Verification
"""

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

from fastapi.testclient import TestClient
from app.main import app
from app.routers.audit import AUDIT_LEDGER


def run_mentor_presentation_demo():
    client = TestClient(app)
    AUDIT_LEDGER.clear()

    print("\n" + "=" * 120)
    print("   LINKIFIC DAY 29 MENTOR LIVE DEMO — FinDoc-AuditEngine v3.0 (Dynamic End-to-End Walkthrough)")
    print("=" * 120)

    # Stage 1: Health Probe
    print("\n[STAGE 1] SYSTEM HEALTH & MODEL TELEMETRY PROBE (GET /health)")
    health = client.get("/health").json()
    print(f"  Status          : {health['status'].upper()}")
    print(f"  Service         : {health['service']} v{health['version']}")
    print(f"  FX Peg Standard : 1 USD = INR {health['pegged_usd_to_inr']:.2f}")
    print(f"  Active Models   : {health['models']}")

    # Stage 2: Raw Text Parsing & PII Scrubbing
    print("\n[STAGE 2] UNSTRUCTURED DOCUMENT PARSING & PRE-INFERENCE PII SCRUBBING (POST /api/v1/audit/parse-raw)")
    raw_sample = (
        "Invoice INV-8841 from Bharat Cloud Infrastructure Ltd; PO: PO-8841; "
        "Total: $740.00; Country: IN; Contact: finance.ap@bharatcloud.in; "
        "Tax PAN: ABCDE1234F; Aadhaar: 2345 6789 0123; Account: 918273645501"
    )
    parsed = client.post("/api/v1/audit/parse-raw", json={"raw_text": raw_sample}).json()
    print(f"  Raw Input       : {raw_sample}")
    print(f"  Sanitized Text  : {parsed['sanitized_text']}")
    print(f"  PII Redactions  : {parsed['pii_redactions_count']} sensitive token(s) masked before ML inference")
    print(f"  Extracted Fields: {parsed['extracted_fields']}")

    # Stage 3: Dynamic Multi-Line Custom Scenario (Not in Benchmark JSON)
    print("\n[STAGE 3] DYNAMIC MULTI-ITEM CUSTOM INVOICE AUDIT (POST /api/v1/audit/process)")
    custom_payload = {
        "invoice": {
            "invoice_id": "INV-DYNAMIC-901",
            "vendor_name": "Kochi Precision Robotics Pvt Ltd",
            "po_number": "PO-DYNAMIC-901",
            "invoice_date": "2026-10-10",
            "due_date": "2026-10-12",  # Rush 2-day settlement window
            "subtotal_usd": 6900.0,
            "tax_usd": 300.0,
            "total_amount_usd": 7200.0,
            "vendor_country": "IN",
            "is_new_vendor": True,
            "vendor_contact_email": "accounts@kochirobotics.in",
            "vendor_pan": "QWERT5678P",
            "items": [
                {"item_id": "ARM-SERVO", "description": "6-Axis Industrial Servo", "quantity": 4, "unit_price_usd": 1350.0},
                {"item_id": "CTRL-PCB", "description": "Motion Controller Board", "quantity": 5, "unit_price_usd": 300.0},
            ],
        },
        "purchase_order": {
            "po_number": "PO-DYNAMIC-901",
            "approved_total_usd": 6500.0,
            "items": [
                {"item_id": "ARM-SERVO", "description": "6-Axis Industrial Servo", "quantity": 4, "unit_price_usd": 1200.0},
                {"item_id": "CTRL-PCB", "description": "Motion Controller Board", "quantity": 5, "unit_price_usd": 300.0},
            ],
            "grn_units_received": {"ARM-SERVO": 4, "CTRL-PCB": 5},
            "grn_units_rejected": {"ARM-SERVO": 0, "CTRL-PCB": 1},  # 1 board damaged at dock
        },
    }
    dyn_res = client.post("/api/v1/audit/process", json=custom_payload).json()
    print(f"  Invoice ID      : {dyn_res['invoice_id']} ({dyn_res['vendor_name']})")
    print(f"  Billed Total    : ${dyn_res['total_amount_usd']:,.2f} USD / INR {dyn_res['total_amount_inr']:,.2f}")
    print(f"  3-Way Variance  : ${dyn_res['variance_amount_usd']:,.2f} USD ({dyn_res['quantity_variance_units']} dock unit rejected)")
    print(f"  ML Risk Score   : {dyn_res['risk_score']:.1f} / 100 ({dyn_res['risk_level']})")
    print(f"  Governance Tier : {dyn_res['approval_tier']} (Authorized={dyn_res['authorized']})")
    print("  Item-Level Diffs:")
    for diff in dyn_res["item_diffs"]:
        print(f"    * {diff['item_id']:<10} | Status: {diff['status']:<22} | Variance: ${diff['line_variance_usd']:,.2f}")
    print("  Perturbation ML Feature Contributions:")
    for fc in dyn_res["feature_contributions"][:3]:
        print(f"    * {fc['feature_name']:<28}: +{fc['risk_contribution']:>4.1f} pts ({fc['feature_value']})")

    # Stage 4: Full 5-Scenario Batch
    print("\n[STAGE 4] EXECUTING 5-SCENARIO ENTERPRISE BENCHMARK BATCH (POST /api/v1/audit/demo-batch)")
    AUDIT_LEDGER.clear()
    batch_res = client.post("/api/v1/audit/demo-batch").json()
    for d in batch_res:
        print(
            f"  - {d['invoice_id']} | ${d['total_amount_usd']:>10,.2f} (INR {d['total_amount_inr']:>12,.2f}) "
            f"| Risk: {d['risk_score']:>4.1f} ({d['risk_level']:<8}) -> {d['approval_tier']}"
        )

    # Stage 5: CSV Compliance Export
    print("\n[STAGE 5] COMPLIANCE AUDIT LEDGER CSV EXPORT (GET /api/v1/audit/export/csv)")
    csv_res = client.get("/api/v1/audit/export/csv")
    csv_lines = csv_res.text.strip().splitlines()
    print(f"  Export Status   : HTTP {csv_res.status_code} ({len(csv_lines) - 1} ledger rows exported)")
    print(f"  CSV Header      : {csv_lines[0]}")
    print(f"  Sample Row 1    : {csv_lines[1][:115]}...")
    print("\n" + "=" * 120)
    print("   MENTOR LIVE DEMO VERIFICATION COMPLETE — ALL STAGES EXECUTED CLEANLY")
    print("=" * 120 + "\n")


if __name__ == "__main__":
    run_mentor_presentation_demo()
