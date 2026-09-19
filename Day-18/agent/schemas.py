"""
Day 18 — AI Agent Schemas and Data Models
Defines structured states, plan representations, tool specifications,
and execution trace models for the Document Research Assistant Agent.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AgentState(str, Enum):
    INITIALIZED = "INITIALIZED"
    PLANNING = "PLANNING"
    TOOL_SELECTION = "TOOL_SELECTION"
    TOOL_EXECUTION = "TOOL_EXECUTION"
    OBSERVING = "OBSERVING"
    DECIDING = "DECIDING"
    FINAL_RESPONSE = "FINAL_RESPONSE"
    FAILED = "FAILED"


class PlanStep(BaseModel):
    step_id: int
    description: str
    target_tool: str
    expected_output: str
    status: str = "pending"  # pending, in_progress, completed, skipped


class ExecutionPlan(BaseModel):
    user_goal: str
    intent: str
    steps: List[PlanStep]


class ToolCall(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    timestamp: str


class ToolResult(BaseModel):
    tool_name: str
    success: bool
    data: Any
    error_message: Optional[str] = None


class TraceStep(BaseModel):
    state: str
    action_or_plan: str
    tool: Optional[str] = None
    observation: Optional[str] = None
    decision: Optional[str] = None
    timestamp: str


class DocumentMetadata(BaseModel):
    document_id: str
    title: str
    category: str
    author: str
    version: str
    char_count: int
    chunk_count: int


class SearchResult(BaseModel):
    document_id: str
    document_title: str
    matched_text: str
    relevance_score: float
    char_start: int
    char_end: int


class AgentResponse(BaseModel):
    question: str
    answer: str
    sources: List[str]
    status: str  # answered, no_relevant_information, error
    plan: List[Dict[str, Any]]
    tools_used: List[str]
    execution_trace: List[Dict[str, Any]]
