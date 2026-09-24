"""
Day 22 — Multi-Agent Communication Protocol & Message Bus
Implements typed, structured inter-agent messaging with:
- Strict contract validation
- Audit logging of message transmissions
- Delivery acknowledgement & error propagation
- Seamless synchronization with Centralized Shared State and persistent JSONL audit trail
"""

import os
import json
import logging
from typing import List, Optional, Callable, Dict
from datetime import datetime, timezone
from .schemas import AgentMessage, AgentRole, MessageType, MessageStatus
from .state import SharedStateManager
from .config import config

logger = logging.getLogger("LinkificMultiAgent.Communication")


class MessageDeliveryError(Exception):
    """Raised when an inter-agent message fails contract validation or routing."""
    pass


class MessageBus:
    """
    In-process asynchronous/synchronous Message Bus mediating communication between agents.
    Logs every message in the active SharedState and writes to the persistent audit log.
    """

    def __init__(self, state_manager: SharedStateManager, audit_file_path: Optional[str] = None):
        self.state_manager = state_manager
        self.audit_file = audit_file_path or config.AUDIT_LOG_FILE
        self._handlers: Dict[AgentRole, Callable[[AgentMessage], None]] = {}

    def register_agent(self, role: AgentRole, handler: Callable[[AgentMessage], None]):
        """Registers an agent's inbound message callback."""
        self._handlers[role] = handler
        logger.debug(f"Agent '{role.value}' registered on MessageBus.")

    def send(self, message: AgentMessage) -> AgentMessage:
        """
        Dispatches an AgentMessage through the bus:
        1. Validates envelope integrity.
        2. Logs message into SharedState message history.
        3. Appends event to persistent activity_audit.jsonl.
        4. Transitions status to DELIVERED.
        5. Invokes receiver handler if registered.
        """
        # Contract validation
        if not message.workflow_id or not message.task_id:
            raise MessageDeliveryError("Message missing required workflow_id or task_id.")
        
        if message.sender == message.receiver:
            raise MessageDeliveryError(f"Agent '{message.sender.value}' cannot send message to itself.")

        # Update status & record in shared state
        message.status = MessageStatus.DELIVERED
        self.state_manager.record_message(message)

        # Append to persistent JSONL audit log
        self._persist_audit_event(message)

        # Deliver to registered agent handler if available
        if message.receiver in self._handlers:
            try:
                self._handlers[message.receiver](message)
                message.status = MessageStatus.PROCESSED
            except Exception as exc:
                message.status = MessageStatus.FAILED
                message.errors.append(f"Handler failure in '{message.receiver.value}': {str(exc)}")
                logger.error(f"Failed delivering message {message.message_id} to {message.receiver.value}: {exc}")
                raise MessageDeliveryError(f"Delivery to {message.receiver.value} failed: {exc}") from exc

        return message

    def create_message(
        self,
        task_id: str,
        sender: AgentRole,
        receiver: AgentRole,
        message_type: MessageType,
        payload: Optional[dict] = None,
        evidence_ids: Optional[List[str]] = None,
        errors: Optional[List[str]] = None
    ) -> AgentMessage:
        """Helper factory creating a strictly validated AgentMessage."""
        return AgentMessage(
            workflow_id=self.state_manager.workflow_id,
            task_id=task_id,
            sender=sender,
            receiver=receiver,
            message_type=message_type,
            status=MessageStatus.SENT,
            payload=payload or {},
            evidence_ids=evidence_ids or [],
            errors=errors or []
        )

    def _persist_audit_event(self, message: AgentMessage):
        """Appends structured JSON record to the persistent audit log file."""
        try:
            os.makedirs(os.path.dirname(self.audit_file), exist_ok=True)
            log_entry = {
                "event": "agent_message_transmitted",
                "timestamp": message.timestamp,
                "message_id": message.message_id,
                "workflow_id": message.workflow_id,
                "task_id": message.task_id,
                "sender": message.sender.value,
                "receiver": message.receiver.value,
                "message_type": message.message_type.value,
                "status": message.status.value,
                "evidence_count": len(message.evidence_ids),
                "error_count": len(message.errors)
            }
            with open(self.audit_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.warning(f"Failed writing audit log to {self.audit_file}: {e}")
