"""
Day 22 — Centralized Shared State Architecture
Implements a thread-safe, audited, role-controlled shared state manager for multi-agent coordination.
Enforces strict field ownership rules, prevents uncontrolled mutations, and logs state transitions.
"""

import threading
import copy
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from .schemas import (
    AgentRole,
    WorkflowStatus,
    ExecutionPlan,
    ResearchFindings,
    AnalysisResult,
    CriticReview,
    WriterReport,
    AgentMessage
)


class StateTransitionRecord(BaseModel):
    """Immutable audit record of a specific shared state mutation."""
    transition_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    actor: AgentRole
    field_modified: str
    previous_state: Optional[str] = None
    new_state: Optional[str] = None
    reason: str


class SharedState(BaseModel):
    """
    Centralized Single Source of Truth for the Multi-Agent System.
    Strictly segregated by agent ownership permissions.
    """
    workflow_id: str
    user_query: str
    context: Dict[str, Any] = Field(default_factory=dict)
    current_status: WorkflowStatus = WorkflowStatus.INITIALIZED

    # Coordinator Owned Fields
    execution_plan: Optional[ExecutionPlan] = None
    revision_count: int = 0
    max_revisions: int = 2
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    agent_statuses: Dict[AgentRole, str] = Field(default_factory=lambda: {
        AgentRole.COORDINATOR: "idle",
        AgentRole.RESEARCH: "idle",
        AgentRole.ANALYZER: "idle",
        AgentRole.CRITIC: "idle",
        AgentRole.WRITER: "idle",
    })

    # Research Agent Owned Fields
    research_findings: Optional[ResearchFindings] = None

    # Analyzer Agent Owned Fields
    analysis_result: Optional[AnalysisResult] = None

    # Critic Agent Owned Fields (List tracks complete revision history)
    critic_reviews: List[CriticReview] = Field(default_factory=list)
    critic_approved: bool = False

    # Writer Agent Owned Fields
    final_report: Optional[WriterReport] = None

    # Communication Audit Log
    message_history: List[AgentMessage] = Field(default_factory=list)

    # State Audit Log
    transition_history: List[StateTransitionRecord] = Field(default_factory=list)

    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class StatePermissionError(Exception):
    """Raised when an agent attempts to mutate a state field outside its permitted scope."""
    pass


class SharedStateManager:
    """
    Thread-safe governor for SharedState operations.
    Enforces role-based write permissions, manages snapshots, and maintains transition history.
    """

    def __init__(self, workflow_id: str, user_query: str, context: Optional[Dict[str, Any]] = None, max_revisions: int = 2):
        self._lock = threading.RLock()
        self._state = SharedState(
            workflow_id=workflow_id,
            user_query=user_query,
            context=context or {},
            max_revisions=max_revisions
        )

    # --------------------------------------------------------------------------
    # Snapshot & Read Access
    # --------------------------------------------------------------------------
    def get_snapshot(self) -> SharedState:
        """Returns an isolated, deep-copied immutable snapshot of current state."""
        with self._lock:
            return copy.deepcopy(self._state)

    @property
    def workflow_id(self) -> str:
        return self._state.workflow_id

    @property
    def current_status(self) -> WorkflowStatus:
        with self._lock:
            return self._state.current_status

    @property
    def revision_count(self) -> int:
        with self._lock:
            return self._state.revision_count

    # --------------------------------------------------------------------------
    # Role-Governed Mutations
    # --------------------------------------------------------------------------
    def update_workflow_status(self, actor: AgentRole, new_status: WorkflowStatus, reason: str = ""):
        """Only Coordinator can transition overall workflow status."""
        with self._lock:
            if actor != AgentRole.COORDINATOR:
                raise StatePermissionError(f"Agent '{actor.value}' is not authorized to modify workflow status.")
            
            prev = self._state.current_status.value
            self._state.current_status = new_status
            self._record_transition(actor, "current_status", prev, new_status.value, reason)

    def set_execution_plan(self, actor: AgentRole, plan: ExecutionPlan):
        """Only Coordinator can set or adjust the execution plan."""
        with self._lock:
            if actor != AgentRole.COORDINATOR:
                raise StatePermissionError(f"Agent '{actor.value}' is not authorized to set the execution plan.")
            
            self._state.execution_plan = plan
            self._record_transition(actor, "execution_plan", None, plan.plan_id, "Initialized execution plan")

    def update_agent_status(self, actor: AgentRole, target_agent: AgentRole, status_label: str):
        """Agents can update their own status; Coordinator can update any agent's status."""
        with self._lock:
            if actor not in (AgentRole.COORDINATOR, target_agent):
                raise StatePermissionError(f"Agent '{actor.value}' cannot update status for '{target_agent.value}'.")
            
            prev = self._state.agent_statuses.get(target_agent, "unknown")
            self._state.agent_statuses[target_agent] = status_label
            self._record_transition(actor, f"agent_statuses[{target_agent.value}]", prev, status_label, "Agent status changed")

    def set_research_findings(self, actor: AgentRole, findings: ResearchFindings):
        """Only Research Agent can populate research findings."""
        with self._lock:
            if actor != AgentRole.RESEARCH:
                raise StatePermissionError(f"Agent '{actor.value}' is not authorized to write research findings.")
            
            self._state.research_findings = findings
            self._record_transition(
                actor,
                "research_findings",
                None,
                f"{len(findings.evidence)} evidence items",
                "Research findings submitted"
            )

    def set_analysis_result(self, actor: AgentRole, analysis: AnalysisResult):
        """Only Analyzer Agent can write analysis output."""
        with self._lock:
            if actor != AgentRole.ANALYZER:
                raise StatePermissionError(f"Agent '{actor.value}' is not authorized to write analysis results.")
            
            self._state.analysis_result = analysis
            self._record_transition(
                actor,
                "analysis_result",
                None,
                f"{len(analysis.key_insights)} insights",
                "Analysis results submitted"
            )

    def add_critic_review(self, actor: AgentRole, review: CriticReview):
        """Only Critic Agent can append a review."""
        with self._lock:
            if actor != AgentRole.CRITIC:
                raise StatePermissionError(f"Agent '{actor.value}' is not authorized to record critic reviews.")
            
            self._state.critic_reviews.append(review)
            self._state.critic_approved = (review.verdict.value == "approved")
            self._record_transition(
                actor,
                "critic_reviews",
                None,
                f"Verdict: {review.verdict.value}, Score: {review.quality_score}",
                review.feedback_summary
            )

    def increment_revision_count(self, actor: AgentRole, reason: str) -> int:
        """Only Coordinator can increment revision iteration count."""
        with self._lock:
            if actor != AgentRole.COORDINATOR:
                raise StatePermissionError(f"Agent '{actor.value}' cannot increment revision count.")
            
            prev = str(self._state.revision_count)
            self._state.revision_count += 1
            self._record_transition(actor, "revision_count", prev, str(self._state.revision_count), reason)
            return self._state.revision_count

    def set_final_report(self, actor: AgentRole, report: WriterReport):
        """Only Writer Agent can produce the final report."""
        with self._lock:
            if actor != AgentRole.WRITER:
                raise StatePermissionError(f"Agent '{actor.value}' is not authorized to write the final report.")
            
            self._state.final_report = report
            self._record_transition(actor, "final_report", None, report.report_id, "Final report generated")

    def record_message(self, message: AgentMessage):
        """Records an inter-agent message into the append-only history."""
        with self._lock:
            self._state.message_history.append(message)

    def add_error(self, actor: AgentRole, error_msg: str):
        with self._lock:
            self._state.errors.append(f"[{actor.value}] {error_msg}")
            self._record_transition(actor, "errors", None, error_msg, "Error logged")

    def add_warning(self, actor: AgentRole, warning_msg: str):
        with self._lock:
            self._state.warnings.append(f"[{actor.value}] {warning_msg}")

    # --------------------------------------------------------------------------
    # Internal Helpers
    # --------------------------------------------------------------------------
    def _record_transition(
        self,
        actor: AgentRole,
        field_modified: str,
        previous_state: Optional[str],
        new_state: Optional[str],
        reason: str
    ):
        record = StateTransitionRecord(
            actor=actor,
            field_modified=field_modified,
            previous_state=previous_state,
            new_state=new_state,
            reason=reason
        )
        self._state.transition_history.append(record)
        self._state.updated_at = datetime.now(timezone.utc).isoformat()
