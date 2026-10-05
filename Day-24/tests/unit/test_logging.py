"""
Unit Tests: Structured Logging Subsystem
Validates JSON formatting, correlation ID propagation, and handler configuration.
"""

import json
import logging
from pathlib import Path
from app.core.logging_config import (
    JSONFormatter,
    TextFormatter,
    set_correlation_id,
    get_correlation_id,
    setup_logging,
    get_logger
)


def test_json_formatter_valid_structure():
    """Verify JSONFormatter outputs valid JSON containing all enterprise telemetry fields."""
    formatter = JSONFormatter(service_name="TestService", environment="test")
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_file.py",
        lineno=42,
        msg="Test event message",
        args=(),
        exc_info=None
    )

    formatted = formatter.format(record)
    data = json.loads(formatted)

    assert data["service"] == "TestService"
    assert data["environment"] == "test"
    assert data["level"] == "INFO"
    assert data["message"] == "Test event message"
    assert data["line_no"] == 42
    assert "timestamp" in data
    assert "correlation_id" in data


def test_correlation_id_context_propagation():
    """Verify correlation ID binds to context and reflects in formatted log records."""
    test_cid = "CORR-TEST-TRACE-99"
    set_correlation_id(test_cid)
    assert get_correlation_id() == test_cid

    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.WARNING,
        pathname="test.py",
        lineno=10,
        msg="Warning event",
        args=(),
        exc_info=None
    )
    data = json.loads(formatter.format(record))
    assert data["correlation_id"] == test_cid


def test_json_formatter_with_exception():
    """Verify JSONFormatter includes stack trace when exc_info is present."""
    formatter = JSONFormatter()
    try:
        raise ValueError("Simulated failure for logging test")
    except ValueError:
        import sys
        exc_info = sys.exc_info()

    record = logging.LogRecord(
        name="test_logger",
        level=logging.ERROR,
        pathname="test.py",
        lineno=25,
        msg="Caught exception",
        args=(),
        exc_info=exc_info
    )
    data = json.loads(formatter.format(record))
    assert "exception" in data
    assert "Simulated failure for logging test" in data["exception"]


def test_text_formatter_output():
    """Verify TextFormatter formats clean string for terminal output."""
    set_correlation_id("CORR-CLI-123")
    formatter = TextFormatter()
    record = logging.LogRecord(
        name="test_cli",
        level=logging.INFO,
        pathname="cli.py",
        lineno=15,
        msg="CLI message",
        args=(),
        exc_info=None
    )
    formatted = formatter.format(record)
    assert "CORR-CLI-123" in formatted
    assert "INFO" in formatted
    assert "CLI message" in formatted


def test_setup_logging_and_get_logger(tmp_path):
    """Verify setup_logging configures root logger and creates rotating log file."""
    log_file = tmp_path / "test_service.log"
    setup_logging(
        level="DEBUG",
        log_format="json",
        log_file_path=str(log_file),
        service_name="TestApp",
        environment="test"
    )

    logger = get_logger("TestLogger")
    logger.info("Verifying file handler write.")

    # Flush handlers
    for h in logging.getLogger().handlers:
        h.flush()

    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert "Verifying file handler write." in content
