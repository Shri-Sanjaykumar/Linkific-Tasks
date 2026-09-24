"""
Day 22 — Inter-Agent Communication & MessageBus Tests
Validates:
- Message envelope integrity and contract enforcement
- Self-transmission rejection
- Agent handler registration and callback delivery
- Delivery status transitions (SENT -> DELIVERED -> PROCESSED)
- Handler failure propagation and error logging
- Persistent activity_audit.jsonl logging
"""

import json
import os
import pytest
from app.communication import MessageBus, MessageDeliveryError
from app.schemas import AgentRole, MessageType, MessageStatus, AgentMessage


def test_message_bus_delivery_success(message_bus, temp_audit_file):
    """Verify clean message dispatch, handler execution, and status transition."""
    received = []

    def dummy_handler(msg: AgentMessage):
        received.append(msg)

    message_bus.register_agent(AgentRole.ANALYZER, dummy_handler)

    msg = message_bus.create_message(
        task_id="TASK-RES-001",
        sender=AgentRole.RESEARCH,
        receiver=AgentRole.ANALYZER,
        message_type=MessageType.RESEARCH_SUBMISSION,
        payload={"docs_found": 3},
        evidence_ids=["DOC-POL-001"]
    )

    result = message_bus.send(msg)

    assert result.status == MessageStatus.PROCESSED
    assert len(received) == 1
    assert received[0].message_id == msg.message_id
    assert received[0].payload["docs_found"] == 3

    # Verify persistent audit log file was written
    assert os.path.exists(temp_audit_file)
    with open(temp_audit_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    assert len(lines) == 1
    audit_data = json.loads(lines[0])
    assert audit_data["event"] == "agent_message_transmitted"
    assert audit_data["sender"] == AgentRole.RESEARCH.value
    assert audit_data["receiver"] == AgentRole.ANALYZER.value
    assert audit_data["evidence_count"] == 1


def test_message_bus_rejects_self_transmission(message_bus):
    """Verify an agent cannot send a message to itself."""
    msg = message_bus.create_message(
        task_id="TASK-ERR-001",
        sender=AgentRole.RESEARCH,
        receiver=AgentRole.RESEARCH,  # Self transmission
        message_type=MessageType.RESEARCH_SUBMISSION
    )

    with pytest.raises(MessageDeliveryError) as exc_info:
        message_bus.send(msg)
    assert "cannot send message to itself" in str(exc_info.value)


def test_message_bus_rejects_empty_ids(message_bus):
    """Verify message with missing workflow_id or task_id is rejected."""
    msg = AgentMessage(
        workflow_id="",  # Empty
        task_id="TASK-01",
        sender=AgentRole.COORDINATOR,
        receiver=AgentRole.RESEARCH,
        message_type=MessageType.TASK_ASSIGNMENT
    )

    with pytest.raises(MessageDeliveryError) as exc_info:
        message_bus.send(msg)
    assert "missing required workflow_id" in str(exc_info.value)


def test_message_bus_handler_failure_handling(message_bus):
    """Verify that an exception in an agent handler marks message as FAILED and raises MessageDeliveryError."""
    def broken_handler(msg: AgentMessage):
        raise ValueError("Simulated handler crash")

    message_bus.register_agent(AgentRole.WRITER, broken_handler)

    msg = message_bus.create_message(
        task_id="TASK-WRI-001",
        sender=AgentRole.COORDINATOR,
        receiver=AgentRole.WRITER,
        message_type=MessageType.TASK_ASSIGNMENT
    )

    with pytest.raises(MessageDeliveryError) as exc_info:
        message_bus.send(msg)

    assert "Delivery to writer_agent failed" in str(exc_info.value)
    assert msg.status == MessageStatus.FAILED
    assert any("Simulated handler crash" in err for err in msg.errors)
