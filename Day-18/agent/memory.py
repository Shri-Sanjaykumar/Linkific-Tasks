"""
Day 18 — Working Memory and Trace Manager
Maintains execution history, tool observations, intermediate decisions,
and context accumulation for the Document Research Assistant Agent.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from .schemas import TraceStep, ToolResult


class AgentMemory:
    """Short-term working memory maintaining conversation state and execution trace."""

    def __init__(self):
        self.question: str = ""
        self.trace: List[TraceStep] = []
        self.tool_results: List[ToolResult] = []
        self.retrieved_contexts: List[str] = []
        self.cited_sources: List[str] = []

    def set_question(self, question: str) -> None:
        self.question = question
        self.trace.clear()
        self.tool_results.clear()
        self.retrieved_contexts.clear()
        self.cited_sources.clear()

    def reset(self) -> None:
        self.question = ""
        self.trace.clear()
        self.tool_results.clear()
        self.retrieved_contexts.clear()
        self.cited_sources.clear()

    def add_trace(
        self,
        state: str,
        action_or_plan: str,
        tool: Optional[str] = None,
        observation: Optional[str] = None,
        decision: Optional[str] = None
    ) -> TraceStep:
        step = TraceStep(
            state=state,
            action_or_plan=action_or_plan,
            tool=tool,
            observation=observation,
            decision=decision,
            timestamp=datetime.now().isoformat()
        )
        self.trace.append(step)
        return step

    def record_tool_result(self, result: ToolResult) -> None:
        self.tool_results.append(result)

    def add_context(self, text: str, source: str) -> None:
        if text not in self.retrieved_contexts:
            self.retrieved_contexts.append(text)
        if source not in self.cited_sources:
            self.cited_sources.append(source)

    def get_source_titles(self) -> List[str]:
        return list(self.cited_sources)

    def get_combined_context(self) -> str:
        return "\n\n".join(self.retrieved_contexts)

    def get_trace_dicts(self) -> List[Dict[str, Any]]:
        return [step.model_dump() for step in self.trace]
