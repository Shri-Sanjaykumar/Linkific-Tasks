"""
Day 22 — Multi-Agent Workflow Engine
Coordinates the complete end-to-end multi-agent execution pipeline:
- Initialization of SharedState & MessageBus
- Dynamic orchestration of Coordinator, Research, Analyzer, Critic, and Writer agents
- Robust revision loop management with max-iteration circuit breaker
- Error boundary containment and detailed execution telemetry compilation
"""

import time
import uuid
import logging
from typing import Dict, Any, Optional

from .schemas import (
    AgentRole,
    WorkflowStatus,
    WorkflowRequest,
    WorkflowResponse,
    CriticVerdict
)
from .config import config
from .state import SharedStateManager
from .communication import MessageBus
from .agents.coordinator_agent import CoordinatorAgent
from .agents.research_agent import ResearchAgent
from .agents.analyzer_agent import AnalyzerAgent
from .agents.critic_agent import CriticAgent
from .agents.writer_agent import WriterAgent

logger = logging.getLogger("LinkificMultiAgent.WorkflowEngine")


class MultiAgentWorkflowEngine:
    """
    Main entrypoint orchestrating the 5-agent collaborative intelligence pipeline.
    """

    def __init__(self, corpus_path: Optional[str] = None, max_revisions: Optional[int] = None):
        self.corpus_path = corpus_path or config.CORPUS_FILE
        self.max_revisions = max_revisions if max_revisions is not None else config.MAX_REVISIONS

    def run(self, query: str, context: Optional[Dict[str, Any]] = None) -> WorkflowResponse:
        """
        Executes the full multi-agent collaborative workflow synchronously.
        """
        start_time = time.perf_counter()
        workflow_id = f"WF-{uuid.uuid4().hex[:8].upper()}"
        
        logger.info(f"Starting Multi-Agent Workflow {workflow_id} for query: '{query}'")

        # 1. Initialize State Manager & Message Bus
        state_mgr = SharedStateManager(
            workflow_id=workflow_id,
            user_query=query,
            context=context or {},
            max_revisions=self.max_revisions
        )
        bus = MessageBus(state_manager=state_mgr)

        # 2. Instantiate Agents
        coordinator = CoordinatorAgent(state_mgr, bus)
        researcher = ResearchAgent(state_mgr, bus, corpus_path=self.corpus_path)
        analyzer = AnalyzerAgent(state_mgr, bus)
        critic = CriticAgent(state_mgr, bus)
        writer = WriterAgent(state_mgr, bus)

        try:
            # ------------------------------------------------------------------
            # Phase 1: Planning
            # ------------------------------------------------------------------
            state_mgr.update_workflow_status(AgentRole.COORDINATOR, WorkflowStatus.PLANNING, "Initiating plan")
            plan = coordinator.execute(task_id="TASK-PLAN-001")

            # ------------------------------------------------------------------
            # Phase 2: Research
            # ------------------------------------------------------------------
            state_mgr.update_workflow_status(AgentRole.COORDINATOR, WorkflowStatus.RESEARCHING, "Starting research")
            researcher.execute(task_id="TASK-RES-002")

            # ------------------------------------------------------------------
            # Phase 3: Analysis
            # ------------------------------------------------------------------
            state_mgr.update_workflow_status(AgentRole.COORDINATOR, WorkflowStatus.ANALYZING, "Starting analysis")
            analyzer.execute(task_id="TASK-ANA-003")

            # ------------------------------------------------------------------
            # Phase 4: Critique & Revision Loop
            # ------------------------------------------------------------------
            state_mgr.update_workflow_status(AgentRole.COORDINATOR, WorkflowStatus.CRITIQUING, "Evaluating quality")
            review = critic.execute(task_id="TASK-CRI-004")

            # Revision Loop
            while True:
                proceed_to_writer, target_agent, focus_terms = coordinator.evaluate_critic_verdict(review)
                if proceed_to_writer:
                    break

                # Increment revision cycle
                rev_idx = state_mgr.increment_revision_count(
                    AgentRole.COORDINATOR,
                    f"Revision triggered for {target_agent.value}"
                )
                state_mgr.update_workflow_status(
                    AgentRole.COORDINATOR,
                    WorkflowStatus.REVISING,
                    f"Executing revision cycle {rev_idx}"
                )
                logger.info(f"Executing revision cycle {rev_idx} targeting '{target_agent.value}'...")

                if target_agent == AgentRole.RESEARCH:
                    # Re-run research with targeted query focus
                    researcher.execute(
                        task_id=f"TASK-RES-REV-{rev_idx}",
                        context={"is_revision": True, "target_focus": focus_terms}
                    )
                    # Re-run analysis on updated evidence
                    analyzer.execute(task_id=f"TASK-ANA-REV-{rev_idx}")
                elif target_agent == AgentRole.ANALYZER:
                    # Re-run analysis with guidance
                    analyzer.execute(
                        task_id=f"TASK-ANA-REV-{rev_idx}",
                        context={"is_revision": True, "focus": focus_terms}
                    )

                # Re-run critique on revised outputs
                review = critic.execute(task_id=f"TASK-CRI-REV-{rev_idx}")

            # ------------------------------------------------------------------
            # Phase 5: Report Synthesis
            # ------------------------------------------------------------------
            state_mgr.update_workflow_status(AgentRole.COORDINATOR, WorkflowStatus.WRITING, "Synthesizing report")
            writer.execute(task_id="TASK-WRI-005")

            # ------------------------------------------------------------------
            # Phase 6: Completion & Telemetry
            # ------------------------------------------------------------------
            state_mgr.update_workflow_status(AgentRole.COORDINATOR, WorkflowStatus.COMPLETED, "Workflow finished")

        except Exception as exc:
            logger.error(f"Workflow {workflow_id} encountered fatal error: {exc}", exc_info=True)
            state_mgr.add_error(AgentRole.COORDINATOR, str(exc))
            state_mgr.update_workflow_status(AgentRole.COORDINATOR, WorkflowStatus.FAILED, f"Fatal error: {exc}")

        elapsed_sec = round(time.perf_counter() - start_time, 3)
        final_snapshot = state_mgr.get_snapshot()

        return WorkflowResponse(
            workflow_id=workflow_id,
            status=final_snapshot.current_status,
            user_query=query,
            final_report=final_snapshot.final_report,
            execution_plan=final_snapshot.execution_plan or plan,
            total_revisions=final_snapshot.revision_count,
            critic_approved=final_snapshot.critic_approved,
            execution_time_seconds=elapsed_sec,
            audit_events_count=len(final_snapshot.message_history),
            warnings=final_snapshot.warnings
        )
