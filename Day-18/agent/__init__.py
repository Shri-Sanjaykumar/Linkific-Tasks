"""
Day 18 — Document Research Assistant Agent Package
A modular, explainable AI Agent architecture featuring planning, tool usage,
memory tracking, and ReAct-style decision making.
"""

from .schemas import (
    AgentState,
    PlanStep,
    ExecutionPlan,
    ToolCall,
    ToolResult,
    TraceStep,
    DocumentMetadata,
    SearchResult,
    AgentResponse
)
from .memory import AgentMemory
from .tools import ToolRegistry, document_search, document_lookup, document_metadata, final_response
from .planner import Planner
from .agent import DocumentResearchAgent

__all__ = [
    "AgentState",
    "PlanStep",
    "ExecutionPlan",
    "ToolCall",
    "ToolResult",
    "TraceStep",
    "DocumentMetadata",
    "SearchResult",
    "AgentResponse",
    "AgentMemory",
    "ToolRegistry",
    "document_search",
    "document_lookup",
    "document_metadata",
    "final_response",
    "Planner",
    "DocumentResearchAgent",
]
