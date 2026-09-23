"""
Day 21 — In-Process Background Tasks & Audit Logger
Implements structured audit logging using FastAPI's native BackgroundTasks.
Provides thread-safe JSON Lines file writing, directory bootstrapping,
error trapping, and pagination for inspection endpoints.

ARCHITECTURAL SCOPE & LIMITATION NOTICE:
FastAPI BackgroundTasks execute in-process within the same worker event loop/threadpool
immediately after the HTTP response has been delivered to the client.
They are suitable for non-critical side effects (activity audit logging, cache warming,
local event telemetry). They are NOT a replacement for durable, distributed task queues
(such as Celery with Redis/RabbitMQ, ARQ, or Kafka) which offer retry policies, worker
isolation, crash durability, and horizontal scaling across servers.
"""

import os
import json
import logging
import threading
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timezone
from .config import settings

logger = logging.getLogger("linkific.api.background")

# Thread lock to guarantee atomic append writes under concurrent task execution
_file_write_lock = threading.Lock()


def ensure_audit_dir(filepath: Optional[str] = None) -> str:
    """Ensures parent directory for audit file exists safely."""
    target_path = filepath or settings.AUDIT_LOG_FILE
    parent_dir = os.path.dirname(os.path.abspath(target_path))
    os.makedirs(parent_dir, exist_ok=True)
    return os.path.abspath(target_path)


def write_audit_log_entry(
    request_id: str,
    event: str,
    endpoint: str,
    status: str,
    duration_ms: float,
    client_ip: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    filepath: Optional[str] = None
) -> bool:
    """
    Executes in-process as a background task.
    Safely serializes an audit record and appends it to the JSON Lines file.
    Does not raise exceptions; logs any I/O failure defensively.
    """
    try:
        target_file = ensure_audit_dir(filepath)

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": request_id,
            "event": event,
            "endpoint": endpoint,
            "status": status,
            "duration_ms": round(duration_ms, 3),
            "client_ip": client_ip or "unknown",
            "metadata": metadata or {}
        }

        line = json.dumps(record) + "\n"

        with _file_write_lock:
            with open(target_file, "a", encoding="utf-8") as f:
                f.write(line)

        logger.debug(f"[{request_id}] Background audit record written to {target_file}")
        return True

    except Exception as e:
        logger.error(f"[{request_id}] Background audit write failed: {type(e).__name__}: {str(e)}")
        return False


def read_audit_logs(
    skip: int = 0,
    limit: int = 20,
    filepath: Optional[str] = None
) -> Tuple[int, List[Dict[str, Any]]]:
    """
    Safely reads and returns paginated audit records from the JSON Lines file.
    Bounded memory access: skips and reads up to limit records.
    """
    target_file = filepath or settings.AUDIT_LOG_FILE
    if not os.path.exists(target_file):
        return 0, []

    records: List[Dict[str, Any]] = []
    total_count = 0

    try:
        with _file_write_lock:
            with open(target_file, "r", encoding="utf-8") as f:
                for line in f:
                    clean = line.strip()
                    if not clean:
                        continue
                    total_count += 1
                    if total_count > skip and len(records) < limit:
                        try:
                            record_dict = json.loads(clean)
                            records.append(record_dict)
                        except json.JSONDecodeError:
                            continue

        return total_count, records

    except Exception as e:
        logger.error(f"Error reading audit log: {str(e)}")
        return 0, []
