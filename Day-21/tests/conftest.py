"""
Day 21 — PyTest Configuration & Shared Fixtures
Configures test-only credentials, test isolation via temporary directories,
and shared TestClient instances.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure Day-21 root is on sys.path
DAY21_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if DAY21_DIR not in sys.path:
    sys.path.insert(0, DAY21_DIR)

# Set test environment variables BEFORE importing settings
os.environ["LINKIFIC_ENV"] = "testing"
os.environ["LINKIFIC_API_KEY"] = "test-standard-api-key"
os.environ["LINKIFIC_ADMIN_API_KEY"] = "test-admin-api-key"

from app.config import settings
from app.main import app

# Update settings in-place for tests
settings.LINKIFIC_ENV = "testing"
settings.LINKIFIC_API_KEY = "test-standard-api-key"
settings.LINKIFIC_ADMIN_API_KEY = "test-admin-api-key"


@pytest.fixture(scope="session")
def test_keys():
    """Provides test API keys for test assertions."""
    return {
        "standard": "test-standard-api-key",
        "admin": "test-admin-api-key",
        "invalid": "invalid-garbage-key-12345"
    }


@pytest.fixture(autouse=True)
def isolate_audit_log(tmp_path):
    """
    Ensures every test runs against an isolated temporary audit file.
    Prevents test contamination of real project data and guarantees clean assertions.
    """
    temp_audit_file = str(tmp_path / "test_activity_audit.jsonl")
    orig_file = settings.AUDIT_LOG_FILE
    settings.AUDIT_LOG_FILE = temp_audit_file
    yield temp_audit_file
    settings.AUDIT_LOG_FILE = orig_file


@pytest.fixture
def client():
    """Provides a synchronous FastAPI TestClient configured for the app."""
    with TestClient(app) as test_client:
        yield test_client
