"""
Day 20 — Schemas & Data Models
Defines Pydantic models for Tool Results, Function Calling definitions,
Execution Tracing, and Tool Chaining.
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
import time
import uuid


class ToolResult(BaseModel):
    """Standard structured envelope for all tool outputs."""
    tool_name: str
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)

    @classmethod
    def ok(cls, tool_name: str, data: Any, metadata: Optional[Dict[str, Any]] = None) -> "ToolResult":
        return cls(
            tool_name=tool_name,
            success=True,
            data=data,
            error=None,
            metadata=metadata or {}
        )

    @classmethod
    def fail(cls, tool_name: str, error: str, metadata: Optional[Dict[str, Any]] = None) -> "ToolResult":
        return cls(
            tool_name=tool_name,
            success=False,
            data=None,
            error=error,
            metadata=metadata or {}
        )


class ToolParameter(BaseModel):
    """Specification of a single parameter accepted by a tool."""
    name: str
    type: str  # "string", "number", "integer", "boolean", "array", "object"
    description: str
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None


class ToolDefinition(BaseModel):
    """Metadata and JSON Schema specification for a callable tool."""
    name: str
    description: str
    parameters: Dict[str, ToolParameter] = Field(default_factory=dict)
    returns: Dict[str, Any] = Field(default_factory=dict)
    is_mock: bool = False
    mock_notice: Optional[str] = None

    def to_json_schema(self) -> Dict[str, Any]:
        """Converts to standard function-calling JSON schema format."""
        properties = {}
        required = []
        for p_name, p_spec in self.parameters.items():
            prop: Dict[str, Any] = {
                "type": p_spec.type,
                "description": p_spec.description
            }
            if p_spec.enum:
                prop["enum"] = p_spec.enum
            if p_spec.default is not None:
                prop["default"] = p_spec.default
            properties[p_name] = prop
            if p_spec.required:
                required.append(p_name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }


class FunctionCallRequest(BaseModel):
    """User request payload for the function-calling engine."""
    user_request: str
    forced_tool: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)


class FunctionCallResult(BaseModel):
    """Complete structured outcome of a function-calling invocation."""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    user_request: str
    selected_tool: Optional[str] = None
    selection_reason: str = ""
    arguments: Dict[str, Any] = Field(default_factory=dict)
    validation_passed: bool = False
    validation_errors: List[str] = Field(default_factory=list)
    tool_result: Optional[ToolResult] = None
    execution_time_ms: float = 0.0
    status: str = "success"  # "success", "validation_error", "execution_error", "unsupported_request"


class TraceStep(BaseModel):
    """A discrete operational step recorded in an execution trace."""
    step_name: str
    status: str  # "ok", "error", "skipped"
    details: Dict[str, Any] = Field(default_factory=dict)
    duration_ms: float = 0.0


class ExecutionTrace(BaseModel):
    """Auditable, concise operational execution trace (without exposing private CoT)."""
    trace_id: str = Field(default_factory=lambda: f"TRC-{uuid.uuid4().hex[:6].upper()}")
    timestamp: str
    user_request: str
    selected_tool: Optional[str] = None
    steps: List[TraceStep] = Field(default_factory=list)
    final_status: str = "completed"
    total_duration_ms: float = 0.0
    summary: str = ""


class ToolChainStep(BaseModel):
    """Single step in a multi-tool chained pipeline."""
    step_number: int
    tool_name: str
    description: str
    input_mapping: Dict[str, Any] = Field(default_factory=dict)
    resolved_arguments: Dict[str, Any] = Field(default_factory=dict)
    output: Optional[ToolResult] = None
    status: str = "pending"  # "pending", "success", "failed"
    duration_ms: float = 0.0


class ToolChainResult(BaseModel):
    """Outcome of an end-to-end chained tool pipeline."""
    chain_name: str
    chain_description: str
    success: bool
    steps: List[ToolChainStep] = Field(default_factory=list)
    final_output: Optional[Any] = None
    error: Optional[str] = None
    total_duration_ms: float = 0.0
