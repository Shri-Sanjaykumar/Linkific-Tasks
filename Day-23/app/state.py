"""
Day 23: State Management & LangGraph TypedDict Schema
Linkific Enterprise Multi-Agent System
"""

import operator
from typing import TypedDict, Annotated, List, Dict, Any, Optional
import time
import uuid

from .schemas import (
    AgentRole,
    MessageType,
    WorkflowStatus,
    Milestone,
    ResearchFindings,
    AnalysisResult,
    CriticReview,
    WriterReport,
    AgentMessage
)


def update_milestones(existing: List[Milestone], new_milestones: List[Milestone]) -> List[Milestone]:
    """
    Reducer function for milestones: updates existing milestone status if step_number matches,
    otherwise appends new milestone.
    """
    if not existing:
        return list(new_milestones)
    if not new_milestones:
        return list(existing)
    
    milestone_map = {m.step_number: m for m in existing}
    for m in new_milestones:
        milestone_map[m.step_number] = m
    return sorted(list(milestone_map.values()), key=lambda m: m.step_number)


class MultiAgentState(TypedDict, total=False):
    """
    Centralized state graph contract managed by LangGraph.
    Channels annotated with reducers aggregate outputs as nodes execute.
    """
    workflow_id: str
    query: str
    mode: str  # "streamlined" or "comprehensive"
    status: WorkflowStatus
    current_agent: AgentRole
    
    # Milestone tracker
    milestones: Annotated[List[Milestone], update_milestones]
    
    # Domain data artifacts
    research_findings: Optional[ResearchFindings]
    analysis_result: Optional[AnalysisResult]
    critic_reviews: Annotated[List[CriticReview], operator.add]
    final_report: Optional[WriterReport]
    final_answer: Optional[str]
    
    # Communication log: every node appends messages here
    communication_log: Annotated[List[AgentMessage], operator.add]
    
    # Operational controls & error boundaries
    revision_count: int
    max_revisions: int
    errors: Annotated[List[str], operator.add]
    next_step: Optional[str]
    execution_start_time: float


def create_initial_state(
    query: str,
    mode: str = "streamlined",
    max_revisions: int = 2,
    workflow_id: Optional[str] = None
) -> MultiAgentState:
    """
    Factory creating a pristine initial state for the LangGraph workflow.
    Appends the inaugural User Request message to the communication log.
    """
    w_id = workflow_id or f"WF-{uuid.uuid4().hex[:8].upper()}"
    
    initial_message = AgentMessage(
        correlation_id=w_id,
        sender=AgentRole.USER,
        recipient=AgentRole.COORDINATOR,
        message_type=MessageType.USER_REQUEST,
        payload={"query": query.strip(), "mode": mode},
        summary=f"User submitted research inquiry: '{query.strip()}'."
    )
    
    return {
        "workflow_id": w_id,
        "query": query.strip(),
        "mode": mode,
        "status": WorkflowStatus.INITIALIZED,
        "current_agent": AgentRole.USER,
        "milestones": [],
        "research_findings": None,
        "analysis_result": None,
        "critic_reviews": [],
        "final_report": None,
        "final_answer": None,
        "communication_log": [initial_message],
        "revision_count": 0,
        "max_revisions": max_revisions,
        "errors": [],
        "next_step": "coordinator",
        "execution_start_time": time.time()
    }
