"""
Day 20 — Utilities Module
Provides serialization, execution trace rendering, and reporting formatters.
"""

import json
import os
from typing import Dict, Any, List
from .schemas import ExecutionTrace, ToolChainResult, FunctionCallResult


def format_execution_trace_markdown(trace: ExecutionTrace) -> str:
    """Renders a structured markdown report for an ExecutionTrace."""
    lines = [
        f"### Operational Execution Trace: `{trace.trace_id}`",
        f"- **Timestamp:** {trace.timestamp}",
        f"- **User Request:** \"{trace.user_request}\"",
        f"- **Selected Tool:** `{trace.selected_tool or 'None (Refused)'}`",
        f"- **Final Status:** `{trace.final_status}`",
        f"- **Total Duration:** `{trace.total_duration_ms:.2f} ms`",
        f"- **Summary:** {trace.summary}",
        "",
        "| Step # | Operational Step | Status | Duration (ms) | Key Step Details |",
        "| :---: | :--- | :---: | :---: | :--- |"
    ]

    for idx, s in enumerate(trace.steps, 1):
        det_str = ", ".join(f"{k}: {v}" for k, v in s.details.items() if v is not None)[:90]
        lines.append(f"| {idx} | `{s.step_name}` | `{s.status}` | {s.duration_ms:.2f} | {det_str} |")

    return "\n".join(lines)


def format_chain_result_markdown(result: ToolChainResult) -> str:
    """Renders a structured markdown report for a ToolChainResult."""
    lines = [
        f"### Tool Chaining Report: `{result.chain_name}`",
        f"- **Description:** {result.chain_description}",
        f"- **Success:** `{'PASSED' if result.success else 'FAILED'}`",
        f"- **Total Duration:** `{result.total_duration_ms:.2f} ms`",
        f"- **Final Output:** `{json.dumps(result.final_output, default=str)[:120] + '...' if result.final_output else 'None'}`",
        "",
        "| Step | Tool Executed | Status | Duration (ms) | Input Mapping / Resolved Args |",
        "| :---: | :--- | :---: | :---: | :--- |"
    ]

    for s in result.steps:
        arg_str = ", ".join(f"{k}={v}" for k, v in s.resolved_arguments.items() if v is not None)[:80]
        lines.append(f"| Step {s.step_number} | `{s.tool_name}` | `{s.status}` | {s.duration_ms:.2f} | `{arg_str}` |")

    return "\n".join(lines)


def save_json_file(data: Any, target_path: str):
    """Safely writes serializable dictionary or Pydantic model to disk as formatted JSON."""
    os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as f:
        if hasattr(data, "model_dump"):
            json.dump(data.model_dump(), f, indent=2, default=str)
        elif isinstance(data, list) and data and hasattr(data[0], "model_dump"):
            json.dump([item.model_dump() for item in data], f, indent=2, default=str)
        else:
            json.dump(data, f, indent=2, default=str)
