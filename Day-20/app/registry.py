"""
Day 20 — Tool Registry Module
Provides centralized registration, schema introspection, argument validation,
and safe execution dispatching for all tools.
"""

from typing import Dict, Any, Callable, List, Optional, Tuple
import inspect
from .schemas import ToolDefinition, ToolParameter, ToolResult


class ToolRegistry:
    """Central registry maintaining tool implementations and schemas."""

    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._definitions: Dict[str, ToolDefinition] = {}

    def register(self, definition: ToolDefinition, func: Callable):
        """Registers a tool implementation alongside its schema definition."""
        self._tools[definition.name] = func
        self._definitions[definition.name] = definition

    def get_tool(self, name: str) -> Optional[Callable]:
        """Retrieves callable for given tool name."""
        return self._tools.get(name)

    def get_definition(self, name: str) -> Optional[ToolDefinition]:
        """Retrieves definition and schema for given tool name."""
        return self._definitions.get(name)

    def list_tools(self) -> List[str]:
        """Lists all registered tool names."""
        return list(self._tools.keys())

    def get_all_definitions(self) -> Dict[str, ToolDefinition]:
        """Returns map of all registered tool definitions."""
        return dict(self._definitions)

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """Exports all registered tools as OpenAI-compatible function schemas."""
        return [defn.to_json_schema() for defn in self._definitions.values()]

    def validate_arguments(self, tool_name: str, arguments: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validates argument dictionary against the registered tool definition.
        Returns (is_valid, list_of_errors).
        """
        defn = self._definitions.get(tool_name)
        if not defn:
            return False, [f"Tool '{tool_name}' is not registered in the registry."]

        errors = []

        # 1. Check required parameters
        for p_name, p_spec in defn.parameters.items():
            if p_spec.required and (p_name not in arguments or arguments[p_name] is None):
                errors.append(f"Missing required parameter '{p_name}'. Description: {p_spec.description}")

        # 2. Check types and enums for provided arguments
        for arg_name, arg_val in arguments.items():
            if arg_name not in defn.parameters:
                # Extra argument: notice or permit
                continue

            p_spec = defn.parameters[arg_name]

            # Type checking
            if arg_val is not None:
                if p_spec.type == "number":
                    if not isinstance(arg_val, (int, float)) or isinstance(arg_val, bool):
                        errors.append(f"Parameter '{arg_name}' must be a number, got {type(arg_val).__name__} ({arg_val}).")
                elif p_spec.type == "integer":
                    if not isinstance(arg_val, int) or isinstance(arg_val, bool):
                        errors.append(f"Parameter '{arg_name}' must be an integer, got {type(arg_val).__name__} ({arg_val}).")
                elif p_spec.type == "string":
                    if not isinstance(arg_val, str):
                        errors.append(f"Parameter '{arg_name}' must be a string, got {type(arg_val).__name__}.")
                elif p_spec.type == "boolean":
                    if not isinstance(arg_val, bool):
                        errors.append(f"Parameter '{arg_name}' must be a boolean, got {type(arg_val).__name__}.")
                elif p_spec.type == "array":
                    if not isinstance(arg_val, (list, tuple)):
                        errors.append(f"Parameter '{arg_name}' must be a list/array, got {type(arg_val).__name__}.")
                elif p_spec.type == "object":
                    if not isinstance(arg_val, (dict, list, str)):
                        errors.append(f"Parameter '{arg_name}' must be an object, dict, or structured data string, got {type(arg_val).__name__}.")

                # Enum checking
                if p_spec.enum and arg_val not in p_spec.enum:
                    errors.append(f"Parameter '{arg_name}' value '{arg_val}' is not in allowed choices: {p_spec.enum}.")

        return (len(errors) == 0, errors)

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """
        Safely executes a registered tool, capturing any runtime exceptions into a ToolResult envelope.
        """
        func = self._tools.get(tool_name)
        if not func:
            return ToolResult.fail(
                tool_name=tool_name,
                error=f"Unsupported or unregistered tool: '{tool_name}'."
            )

        # Validate arguments first
        is_valid, errs = self.validate_arguments(tool_name, arguments)
        if not is_valid:
            return ToolResult.fail(
                tool_name=tool_name,
                error=f"Argument validation failed: {'; '.join(errs)}",
                metadata={"validation_errors": errs}
            )

        try:
            # Execute tool implementation
            res = func(**arguments)
            if isinstance(res, ToolResult):
                return res
            else:
                return ToolResult.ok(tool_name=tool_name, data=res)
        except ZeroDivisionError as zde:
            return ToolResult.fail(
                tool_name=tool_name,
                error=f"ZeroDivisionError: {str(zde)}"
            )
        except Exception as e:
            return ToolResult.fail(
                tool_name=tool_name,
                error=f"Execution error in '{tool_name}': {str(e)}"
            )


# Global singleton registry instance
default_registry = ToolRegistry()
