"""
Day 21 — Tests for In-Process Background Tasks & Audit File Logging
"""

import os
import json
import threading
from app.background_tasks import write_audit_log_entry, read_audit_logs


def test_write_audit_log_entry_success(tmp_path):
    """Verify write_audit_log_entry creates structured JSON Lines records."""
    audit_file = str(tmp_path / "custom_audit.jsonl")

    success = write_audit_log_entry(
        request_id="test-req-001",
        event="test_event",
        endpoint="/test",
        status="success",
        duration_ms=12.5,
        client_ip="127.0.0.1",
        metadata={"user": "tester"},
        filepath=audit_file
    )

    assert success is True
    assert os.path.exists(audit_file)

    with open(audit_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["request_id"] == "test-req-001"
    assert record["event"] == "test_event"
    assert record["duration_ms"] == 12.5
    assert record["metadata"]["user"] == "tester"


def test_read_audit_logs_pagination(tmp_path):
    """Verify read_audit_logs correctly paginates records."""
    audit_file = str(tmp_path / "paginate_audit.jsonl")

    # Write 5 entries
    for i in range(5):
        write_audit_log_entry(
            request_id=f"req-{i}",
            event="query",
            endpoint="/test",
            status="success",
            duration_ms=float(i * 10),
            filepath=audit_file
        )

    # Read page 1: skip 0, limit 2
    total, page1 = read_audit_logs(skip=0, limit=2, filepath=audit_file)
    assert total == 5
    assert len(page1) == 2
    assert page1[0]["request_id"] == "req-0"
    assert page1[1]["request_id"] == "req-1"

    # Read page 2: skip 2, limit 2
    total, page2 = read_audit_logs(skip=2, limit=2, filepath=audit_file)
    assert total == 5
    assert len(page2) == 2
    assert page2[0]["request_id"] == "req-2"
    assert page2[1]["request_id"] == "req-3"


def test_read_audit_logs_non_existent_file():
    """Verify reading a non-existent file returns 0 and empty list cleanly."""
    total, records = read_audit_logs(filepath="non_existent_audit_file.jsonl")
    assert total == 0
    assert records == []


def test_read_audit_logs_skips_malformed_lines(tmp_path):
    """Verify corrupt/malformed lines in audit file are skipped without failing."""
    audit_file = str(tmp_path / "corrupt_audit.jsonl")
    with open(audit_file, "w", encoding="utf-8") as f:
        f.write('{"request_id": "valid-1", "event": "ev1"}\n')
        f.write('MALFORMED_CORRUPTED_JSON_LINE\n')
        f.write('{"request_id": "valid-2", "event": "ev2"}\n')

    total, records = read_audit_logs(filepath=audit_file)
    assert total == 3  # total non-empty lines
    assert len(records) == 2  # 2 valid parsed JSON objects
    assert records[0]["request_id"] == "valid-1"
    assert records[1]["request_id"] == "valid-2"


def test_concurrent_audit_writes(tmp_path):
    """Verify multiple concurrent threads writing to audit file do not corrupt data."""
    audit_file = str(tmp_path / "concurrent_audit.jsonl")
    num_threads = 10
    writes_per_thread = 5

    def _worker(thread_idx):
        for i in range(writes_per_thread):
            write_audit_log_entry(
                request_id=f"thread-{thread_idx}-op-{i}",
                event="concurrent_test",
                endpoint="/test",
                status="success",
                duration_ms=1.0,
                filepath=audit_file
            )

    threads = [threading.Thread(target=_worker, args=(t,)) for t in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Verify all lines were written and all are valid JSON
    with open(audit_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    assert len(lines) == num_threads * writes_per_thread
    for line in lines:
        parsed = json.loads(line)
        assert "thread-" in parsed["request_id"]


def test_endpoint_triggers_background_audit_log(client, test_keys, isolate_audit_log):
    """Verify invoking /api/v1/query enqueues background task writing to audit log."""
    payload = {"question": "What are the core collaboration hours?"}
    response = client.post(
        "/api/v1/query",
        json=payload,
        headers={"X-API-Key": test_keys["standard"], "X-Request-ID": "audit-trace-777"}
    )
    assert response.status_code == 200

    # Read records from the isolated audit log file
    total, records = read_audit_logs(skip=0, limit=10, filepath=isolate_audit_log)
    assert total >= 1
    matched = [r for r in records if r["request_id"] == "audit-trace-777"]
    assert len(matched) == 1
    assert matched[0]["event"] == "query_completed"
    assert matched[0]["status"] == "success"
