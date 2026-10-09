"""End-to-End System Regression Suite for FinDoc-AuditEngine.

Ensures 100% backward compatibility and exact governance tier decisions across
all 5 enterprise benchmark test scenarios.
"""

import json
from pathlib import Path
from fastapi.testclient import TestClient

from app.models import ApprovalTierEnum


def test_full_benchmark_regression_suite(client: TestClient):
    """Execute end-to-end audit processing for all 5 enterprise benchmark invoices."""
    data_path = Path(__file__).resolve().parent.parent / "data" / "benchmark_invoices.json"
    with open(data_path, "r", encoding="utf-8") as f:
        benchmarks = json.load(f)

    assert len(benchmarks) == 5

    expected_results = {
        "INV-1001": {
            "tier": ApprovalTierEnum.TIER_1_STP,
            "authorized": True,
            "amount_usd": 432.0,
            "amount_inr": 37368.0,
            "requires_hitl": False,
        },
        "INV-1002": {
            "tier": ApprovalTierEnum.TIER_2_MANAGER,
            "authorized": True,
            "amount_usd": 4860.0,
            "amount_inr": 420390.0,
            "requires_hitl": True,
        },
        "INV-1003": {
            "tier": ApprovalTierEnum.TIER_3_DIRECTOR,
            "authorized": True,
            "amount_usd": 27000.0,
            "amount_inr": 2335500.0,
            "requires_hitl": True,
        },
        "INV-1004": {
            "tier": ApprovalTierEnum.REJECTED_DISCREPANCY,
            "authorized": False,
            "amount_usd": 5400.0,
            "amount_inr": 467100.0,
            "requires_hitl": True,
        },
        "INV-1005": {
            "tier": ApprovalTierEnum.FROZEN_FRAUD_RISK,
            "authorized": False,
            "amount_usd": 49500.0,
            "amount_inr": 4281750.0,
            "requires_hitl": True,
        },
    }

    for item in benchmarks:
        payload = {
            "invoice": item["invoice"],
            "purchase_order": item.get("po"),
        }
        response = client.post("/api/v1/audit/process", json=payload)
        assert response.status_code == 200, f"Failed for {item['invoice']['invoice_id']}: {response.text}"
        data = response.json()

        inv_id = data["invoice_id"]
        exp = expected_results[inv_id]

        assert data["approval_tier"] == exp["tier"].value
        assert data["authorized"] == exp["authorized"]
        assert data["total_amount_usd"] == exp["amount_usd"]
        assert data["total_amount_inr"] == exp["amount_inr"]
        assert data["requires_hitl"] == exp["requires_hitl"]

    # Verify portfolio aggregate metrics
    summary_res = client.get("/api/v1/audit/summary")
    assert summary_res.status_code == 200
    summary = summary_res.json()

    assert summary["total_invoices_audited"] == 5
    assert summary["total_disbursed_usd"] == 32292.00
    assert summary["total_disbursed_inr"] == 2793258.00
    assert summary["blocked_invoices_count"] == 2
    assert summary["stp_rate_percentage"] == 20.0
    assert summary["exchange_rate_applied"] == 86.50
