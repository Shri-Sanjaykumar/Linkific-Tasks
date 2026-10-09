"""Enterprise Custom Domain Exceptions for FinDoc-AuditEngine.

Provides strongly-typed domain errors with standard HTTP mapping and machine-readable error codes.
"""

from typing import Any, Dict, Optional


class FinDocAuditException(Exception):
    """Base exception for all financial document audit domain errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "ERR_AUDIT_INTERNAL",
        http_status: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.http_status = http_status
        self.details = details or {}


class ReconciliationError(FinDocAuditException):
    """Raised when mathematical 3-way reconciliation fails or payload items are corrupted."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="ERR_RECONCILIATION_FAILED",
            http_status=422,
            details=details,
        )


class POCommitmentNotFoundError(FinDocAuditException):
    """Raised when an invoice references a Purchase Order absent from corporate commitments."""

    def __init__(self, po_number: str):
        super().__init__(
            message=f"Purchase Order '{po_number}' was not found in corporate commitments ledger.",
            error_code="ERR_PO_NOT_FOUND",
            http_status=404,
            details={"po_number": po_number},
        )


class AnomalyDetectionError(FinDocAuditException):
    """Raised when ML feature extraction or Isolation Forest scoring encounters invalid telemetry."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="ERR_ML_ANOMALY_ENGINE",
            http_status=500,
            details=details,
        )


class GovernancePolicyViolation(FinDocAuditException):
    """Raised when an invoice violates non-negotiable enterprise compliance standards."""

    def __init__(self, message: str, tier: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="ERR_POLICY_VIOLATION",
            http_status=403,
            details={"tier": tier, **(details or {})},
        )
