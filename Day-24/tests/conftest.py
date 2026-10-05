"""
Linkific Enterprise AI Service - PyTest Test Configuration & Fixtures
"""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure Day-24 root is on PYTHONPATH
day24_root = Path(__file__).resolve().parent.parent
if str(day24_root) not in sys.path:
    sys.path.insert(0, str(day24_root))

from app.main import create_app
from app.core.config import get_settings, Settings
from app.core.metrics import metrics_registry


@pytest.fixture(scope="session")
def app_instance():
    """Provides a fresh FastAPI test application instance."""
    app = create_app()
    return app


@pytest.fixture(scope="session")
def client(app_instance):
    """Provides an HTTP test client for API endpoint integration testing."""
    with TestClient(app_instance) as c:
        yield c


@pytest.fixture
def auth_headers():
    """Provides valid authorization headers using active test settings."""
    settings = get_settings()
    return {"X-API-Key": settings.API_KEY}


@pytest.fixture
def sample_workflow_request():
    """Sample valid streamlined workflow request payload."""
    return {
        "query": "What are the corporate guidelines regarding remote work, hardware allowances, and core collaboration hours?",
        "mode": "streamlined"
    }


@pytest.fixture
def sample_finance_request():
    """Sample valid finance invoice approval request payload."""
    return {
        "invoice_id": "INV-2026-9081",
        "po_number": "PO-98214",
        "vendor_name": "Cloud Infra Solutions Pvt Ltd",
        "amount": 750.00,
        "currency": "USD",
        "line_items": [
            {
                "item_name": "Compute Engine Instances",
                "quantity": 1,
                "unit_price": 750.00,
                "total_price": 750.00
            }
        ],
        "submitted_by": "billing-automation@linkific.in"
    }
