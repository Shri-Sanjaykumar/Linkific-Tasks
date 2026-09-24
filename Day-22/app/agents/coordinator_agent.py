"""
Day 22 — Coordinator Agent Implementation
Responsibilities:
- Master orchestrator and workflow planner for the multi-agent system.
- Translates user query into a milestone-based ExecutionPlan.
- Directs execution order and inter-agent message passing via MessageBus.
- Evaluates Critic Agent reviews and manages revision loops.
- Enforces max revision safety caps and circuit breakers.
- Conducts final validation and compiles end-to-end telemetry.
"""

import time
import logging
from typing import Dict, Any, Optional, List
from .base import BaseAgent
from ..schemas import (
    AgentRole,
    MessageType,
    WorkflowStatus,
    ExecutionPlan,
    ExecutionMilestone,
    CriticVerdict,
    WorkflowResponse
)

logger = logging.getLogger("LinkificMultiAgent.CoordinatorAgent")


class CoordinatorAgent(BaseAgent):
    """
    Central orchestration and planning intelligence.
    Guarantees reliable execution order, handles errors, and enforces validation gates.
    """

    def __init__(self, state_manager, bus):
        super().__init__(AgentRole.COORDINATOR, state_manager, bus)

    def create_plan(self, query: str) -> ExecutionPlan:
        """Constructs a deterministic execution plan with numbered milestones."""
        plan = ExecutionPlan(
            goal=f"Investigate enterprise topic: '{query}'",
            milestones=[
                ExecutionMilestone(
                    step_number=1,
                    task_id="TASK-PLAN-001",
                    assigned_agent=AgentRole.COORDINATOR,
                    description="Analyze user request and construct execution topology."
                ),
                ExecutionMilestone(
                    step_number=2,
                    task_id="TASK-RES-002",
                    assigned_agent=AgentRole.RESEARCH,
                    description="Retrieve grounded evidence from enterprise document corpus."
                ),
                ExecutionMilestone(
                    step_number=3,
                    task_id="TASK-ANA-003",
                    assigned_agent=AgentRole.ANALYZER,
                    description="Derive structured insights, correlations, and thematic clusters."
                ),
                ExecutionMilestone(
                    step_number=4,
                    task_id="TASK-CRI-004",
                    assigned_agent=AgentRole.CRITIC,
                    description="Conduct adversarial review for citations, support, and hallucinations."
                ),
                ExecutionMilestone(
                    step_number=5,
                    task_id="TASK-WRI-005",
                    assigned_agent=AgentRole.WRITER,
                    description="Synthesize verified findings into executive enterprise intelligence report."
                ),
                ExecutionMilestone(
                    step_number=6,
                    task_id="TASK-FIN-006",
                    assigned_agent=AgentRole.COORDINATOR,
                    description="Verify final deliverables, compile audit telemetry, and terminate workflow."
                )
            ]
        )
        self.state_manager.set_execution_plan(self.role, plan)
        return plan

    def execute(self, task_id: str, context: Optional[Dict[str, Any]] = None) -> ExecutionPlan:
        """Initiates planning phase."""
        self.state_manager.update_agent_status(self.role, self.role, "planning")
        snapshot = self.state_manager.get_snapshot()
        plan = self.create_plan(snapshot.user_query)
        self.state_manager.update_agent_status(self.role, self.role, "completed")
        return plan

    def evaluate_critic_verdict(self, review) -> tuple[bool, Optional[AgentRole], List[str]]:
        """
        Decides whether to proceed to Writer or execute a revision loop.
        Returns: (should_proceed_to_writer, target_agent_for_revision, keywords_to_focus)
        """
        snapshot = self.state_manager.get_snapshot()

        if review.verdict == CriticVerdict.APPROVED:
            logger.info("Critic review APPROVED. Directing workflow to Writer Agent.")
            return True, None, []

        # Check revision budget
        if snapshot.revision_count >= snapshot.max_revisions:
            logger.warning(
                f"Max revision limit reached ({snapshot.max_revisions}). "
                "Applying circuit breaker: proceeding to Writer with qualification disclosure."
            )
            self.state_manager.add_warning(
                self.role,
                f"Max revision cycles ({snapshot.max_revisions}) reached without unconditional Critic approval. "
                "Proceeding with qualified partial findings."
            )
            return True, None, []

        # Determine target agent for revision
        target_agent = AgentRole.RESEARCH
        focus_terms = []

        for defect in review.defects:
            if defect.target_agent == AgentRole.RESEARCH:
                target_agent = AgentRole.RESEARCH
                # Extract any quoted or specific focus terms
                focus_terms.append(defect.actionable_correction)
            elif defect.target_agent == AgentRole.ANALYZER and target_agent != AgentRole.RESEARCH:
                target_agent = AgentRole.ANALYZER

        return False, target_agent, focus_terms
