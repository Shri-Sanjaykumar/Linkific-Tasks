"""
Linkific Enterprise AI Service - Structured Logging Subsystem
Provides JSON-structured, audit-compliant logging with correlation ID tracing.
"""

import os
import sys
import json
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from contextvars import ContextVar

# Thread-safe ContextVar to preserve correlation IDs across asynchronous request contexts
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="SYSTEM")


def get_correlation_id() -> str:
    """Retrieve the active correlation ID for the current async execution context."""
    return correlation_id_ctx.get()


def set_correlation_id(corr_id: str) -> None:
    """Bind a correlation ID to the current async execution context."""
    correlation_id_ctx.set(corr_id)


class JSONFormatter(logging.Formatter):
    """
    Serializes standard Python LogRecord objects into structured JSON strings.
    Compatible with modern log aggregators (Elasticsearch, CloudWatch, Datadog).
    """

    def __init__(self, service_name: str = "LinkificEnterpriseService", environment: str = "production"):
        super().__init__()
        self.service_name = service_name
        self.environment = environment

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": self.service_name,
            "environment": self.environment,
            "correlation_id": get_correlation_id(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line_no": record.lineno,
            "message": record.getMessage(),
        }

        # Include stack trace if exception exists
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Include custom extra metadata if passed to logger
        custom_extras = {
            k: v for k, v in record.__dict__.items()
            if k not in {
                "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
                "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
                "created", "msecs", "relativeCreated", "thread", "threadName",
                "processName", "process", "message"
            }
        }
        if custom_extras:
            log_entry["extra"] = custom_extras

        return json.dumps(log_entry, default=str)


class TextFormatter(logging.Formatter):
    """Human-readable formatter with correlation ID for local terminal debugging."""

    def format(self, record: logging.LogRecord) -> str:
        cid = get_correlation_id()
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        prefix = f"[{timestamp}] [{record.levelname:<8}] [cid={cid}] [{record.name}:{record.lineno}]"
        msg = f"{prefix} {record.getMessage()}"
        if record.exc_info:
            msg += f"\n{self.formatException(record.exc_info)}"
        return msg


def setup_logging(
    level: str = "INFO",
    log_format: str = "json",
    log_file_path: Optional[str] = "data/service.log",
    service_name: str = "LinkificEnterpriseService",
    environment: str = "development",
    max_bytes: int = 10485760,
    backup_count: int = 5
) -> None:
    """
    Configures application logging with both console and rotating file handlers.
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers to prevent duplicate logging
    root_logger.handlers.clear()

    # Formatter selection
    if log_format.lower() == "json":
        formatter = JSONFormatter(service_name=service_name, environment=environment)
    else:
        formatter = TextFormatter()

    # 1. Console Stream Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 2. Rotating File Handler (Production Audit Trail)
    if log_file_path:
        log_dir = os.path.dirname(log_file_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        file_handler = RotatingFileHandler(
            filename=log_file_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        file_handler.setLevel(log_level)
        # Always write JSON to file for structured indexing
        file_handler.setFormatter(JSONFormatter(service_name=service_name, environment=environment))
        root_logger.addHandler(file_handler)

    # Quiet external verbose loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Obtain a named logger instance configured with application standards."""
    return logging.getLogger(name)
