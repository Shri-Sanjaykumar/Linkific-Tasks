"""
Day 20 — Calculator Tool
Performs basic arithmetic operations with strict type checks,
division-by-zero protection, and structured responses.
"""

from typing import Union, Dict, Any
from ..schemas import ToolResult, ToolDefinition, ToolParameter


def calculator_tool(
    a: Union[int, float],
    b: Union[int, float],
    operation: str
) -> ToolResult:
    """
    Executes an arithmetic operation on two numeric operands.
    Supports: add, subtract, multiply, divide.
    """
    # 1. Type validation
    if not isinstance(a, (int, float)) or isinstance(a, bool):
        return ToolResult.fail("calculator", f"Operand 'a' must be a numeric value, got {type(a).__name__}.")
    if not isinstance(b, (int, float)) or isinstance(b, bool):
        return ToolResult.fail("calculator", f"Operand 'b' must be a numeric value, got {type(b).__name__}.")

    op = str(operation).strip().lower()

    # 2. Operation validation & execution
    if op in ("add", "addition", "+"):
        result = a + b
        normalized_op = "add"
    elif op in ("subtract", "subtraction", "-"):
        result = a - b
        normalized_op = "subtract"
    elif op in ("multiply", "multiplication", "*"):
        result = a * b
        normalized_op = "multiply"
    elif op in ("divide", "division", "/"):
        if b == 0:
            return ToolResult.fail(
                "calculator",
                "Division by zero is not allowed.",
                metadata={"operation": "divide", "a": a, "b": b}
            )
        result = a / b
        normalized_op = "divide"
    else:
        return ToolResult.fail(
            "calculator",
            f"Unsupported operation '{operation}'. Supported operations are: 'add', 'subtract', 'multiply', 'divide'.",
            metadata={"operation": operation}
        )

    # Format result: if whole integer float, convert to float or int cleanly
    formatted_result = int(result) if isinstance(result, float) and result.is_integer() else round(result, 6)

    return ToolResult.ok(
        "calculator",
        data={
            "operation": normalized_op,
            "a": a,
            "b": b,
            "result": formatted_result
        },
        metadata={"execution_type": "deterministic_math"}
    )


CALCULATOR_DEFINITION = ToolDefinition(
    name="calculator",
    description="Performs arithmetic calculations (+, -, *, /) between two numbers with division-by-zero protection.",
    parameters={
        "a": ToolParameter(
            name="a",
            type="number",
            description="First operand (number).",
            required=True
        ),
        "b": ToolParameter(
            name="b",
            type="number",
            description="Second operand (number).",
            required=True
        ),
        "operation": ToolParameter(
            name="operation",
            type="string",
            description="Arithmetic operation to perform.",
            required=True,
            enum=["add", "subtract", "multiply", "divide"]
        )
    },
    returns={
        "type": "object",
        "properties": {
            "operation": {"type": "string"},
            "a": {"type": "number"},
            "b": {"type": "number"},
            "result": {"type": "number"}
        }
    },
    is_mock=False
)
