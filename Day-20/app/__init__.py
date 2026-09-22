"""
Day 20 — Function Calling, Tool Creation, Tool Chaining, and Error Handling
"""

from .schemas import (
    ToolResult,
    ToolDefinition,
    ToolParameter,
    FunctionCallRequest,
    FunctionCallResult,
    ExecutionTrace,
    ToolChainResult,
    ToolChainStep
)
from .registry import ToolRegistry, default_registry
from .engine import FunctionCallingEngine
from .chains import ToolChainPipeline
from .tools import register_all_tools

__all__ = [
    "ToolResult",
    "ToolDefinition",
    "ToolParameter",
    "FunctionCallRequest",
    "FunctionCallResult",
    "ExecutionTrace",
    "ToolChainResult",
    "ToolChainStep",
    "ToolRegistry",
    "default_registry",
    "FunctionCallingEngine",
    "ToolChainPipeline",
    "register_all_tools"
]
