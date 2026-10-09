"""PyTest Configuration and Shared Test Fixtures for FinDoc-AuditEngine."""

import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure Day-28 root directory is on sys.path
TESTS_DIR = Path(__file__).resolve().parent
ROOT_DIR = TESTS_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.main import app
from app.routers.audit import AUDIT_LEDGER, PURCHASE_ORDERS


@pytest.fixture(autouse=True)
def clean_audit_state():
    """Reset audit ledger and PO memory before each test run."""
    AUDIT_LEDGER.clear()
    PURCHASE_ORDERS.clear()
    yield
    AUDIT_LEDGER.clear()
    PURCHASE_ORDERS.clear()


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    return TestClient(app)
