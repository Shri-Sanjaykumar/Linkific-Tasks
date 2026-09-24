"""
Day 22 — Abstract Base Agent Definition
Establishes the foundation for all specialized agents:
- Lifecycle tracking
- Contract validation
- Error boundary isolation
- Audited shared state access
"""

import abc
import logging
from typing import Dict, Any, Optional
from ..schemas import AgentRole, AgentMessage, MessageType
from ..state import SharedStateManager
from ..communication import MessageBus

logger = logging.getLogger("LinkificMultiAgent.BaseAgent")


class BaseAgent(abc.ABC):
    """
    Abstract contract governing all multi-agent participants.
    Standardizes state interaction, messaging, and execution telemetry.
    """

    def __init__(self, role: AgentRole, state_manager: SharedStateManager, bus: MessageBus):
        self.role = role
        self.state_manager = state_manager
        self.bus = bus
        self.bus.register_agent(self.role, self.handle_message)

    def handle_message(self, message: AgentMessage) -> None:
        """Default message ingress handler. Can be extended by subclasses."""
        logger.debug(f"Agent [{self.role.value}] received message {message.message_id} from {message.sender.value}")

    @abc.abstractmethod
    def execute(self, task_id: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Core execution logic specific to the agent's assigned role."""
        pass

    def send_output(
        self,
        task_id: str,
        receiver: AgentRole,
        message_type: MessageType,
        payload: Dict[str, Any],
        evidence_ids: Optional[list] = None
    ) -> AgentMessage:
        """Constructs and dispatches an outbound typed message to another agent."""
        msg = self.bus.create_message(
            task_id=task_id,
            sender=self.role,
            receiver=receiver,
            message_type=message_type,
            payload=payload,
            evidence_ids=evidence_ids or []
        )
        return self.bus.send(msg)
