"""Tests for Custom Domain Exceptions and Global Error Handlers."""

import pytest
from fastapi.testclient import TestClient

from app.exceptions import (
    AnomalyDetectionError,
    FinDocAuditException,
    GovernancePolicyViolation,
    POCommitmentNotFoundError,
    ReconciliationError,
)
from app.main import app


def test_exception_hierarchy():
    """Verify that all domain exceptions derive from FinDocAuditException with valid HTTP codes."""
    rec_err = ReconciliationError("Variance threshold exceeded", {"delta": 50.0})
    assert isinstance(rec_err, FinDocAuditException)
    assert rec_err.http_status == 422
    assert rec_err.error_code == "ERR_RECONCILIATION_FAILED"
    assert rec_err.details["delta"] == 50.0

    po_err = POCommitmentNotFoundError("PO-12345")
    assert isinstance(po_err, FinDocAuditException)
    assert po_err.http_status == 404
    assert po_err.error_code == "ERR_PO_NOT_FOUND"

    gov_err = GovernancePolicyViolation("Sanctioned vendor country", tier="FROZEN_FRAUD_RISK")
    assert isinstance(gov_err, FinDocAuditException)
    assert gov_err.http_status == 403
    assert gov_err.error_code == "ERR_POLICY_VIOLATION"

    ml_err = AnomalyDetectionError("Feature matrix contains NaN")
    assert isinstance(ml_err, FinDocAuditException)
    assert ml_err.http_status == 500
    assert ml_err.error_code == "ERR_ML_ANOMALY_ENGINE"


def test_global_exception_handler_integration(client: TestClient):
    """Verify that any route throwing a FinDocAuditException produces structured RFC-compliant JSON."""
    # Temporarily attach a test endpoint that triggers a custom exception
    @app.get("/api/v1/audit/test-exception")
    def trigger_test_exception():
        raise POCommitmentNotFoundError("PO-TEST-MISSING")

    response = client.get("/api/v1/audit/test-exception")
    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "ERR_PO_NOT_FOUND"
    assert "PO-TEST-MISSING" in data["message"]
    assert "timestamp" in data
    assert "details" in data
