"""
Day 20 — Date & Time Tool
Performs deterministic calendar calculations, ISO 8601 validation,
date difference, date addition/subtraction, and timezone handling.
"""

from datetime import datetime, date, timedelta, timezone
from typing import Optional, Dict, Any
from ..schemas import ToolResult, ToolDefinition, ToolParameter


def _parse_iso_date(date_str: str) -> Optional[datetime]:
    """Strictly parses YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS format."""
    if not date_str or not isinstance(date_str, str):
        return None
    s = date_str.strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def date_tool(
    operation: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    days: Optional[int] = None,
    tz_name: str = "UTC"
) -> ToolResult:
    """
    Handles temporal operations:
    - 'current_date': Returns current date (YYYY-MM-DD).
    - 'current_datetime': Returns current ISO timestamp.
    - 'date_diff': Calculates difference in days/hours between start_date and end_date.
    - 'add_days': Adds integer days to start_date.
    - 'subtract_days': Subtracts integer days from start_date.
    """
    op = str(operation).strip().lower()

    # Timezone resolution
    tz = timezone.utc
    tz_label = "UTC"

    # 1. Current timestamp operations
    if op == "current_date":
        now = datetime.now(tz)
        return ToolResult.ok(
            "date_tool",
            data={
                "operation": "current_date",
                "date": now.strftime("%Y-%m-%d"),
                "timezone": tz_label
            }
        )

    elif op == "current_datetime":
        now = datetime.now(tz)
        return ToolResult.ok(
            "date_tool",
            data={
                "operation": "current_datetime",
                "datetime": now.isoformat(),
                "timezone": tz_label
            }
        )

    # 2. Date difference operation
    elif op in ("date_diff", "difference"):
        if not start_date or not end_date:
            return ToolResult.fail("date_tool", "Operation 'date_diff' requires both 'start_date' and 'end_date' parameters.")

        dt_start = _parse_iso_date(start_date)
        if dt_start is None:
            return ToolResult.fail(
                "date_tool",
                f"Invalid 'start_date' format: '{start_date}'. Must be valid ISO format 'YYYY-MM-DD'.",
                metadata={"start_date": start_date}
            )

        dt_end = _parse_iso_date(end_date)
        if dt_end is None:
            return ToolResult.fail(
                "date_tool",
                f"Invalid 'end_date' format: '{end_date}'. Must be valid ISO format 'YYYY-MM-DD'.",
                metadata={"end_date": end_date}
            )

        diff = dt_end - dt_start
        total_seconds = int(diff.total_seconds())
        days_diff = diff.days
        hours_diff = total_seconds // 3600

        return ToolResult.ok(
            "date_tool",
            data={
                "operation": "date_diff",
                "start_date": dt_start.strftime("%Y-%m-%d"),
                "end_date": dt_end.strftime("%Y-%m-%d"),
                "days_difference": days_diff,
                "hours_difference": hours_diff,
                "is_positive": days_diff >= 0
            },
            metadata={"timezone": tz_label}
        )

    # 3. Add days operation
    elif op in ("add_days", "add"):
        if not start_date:
            return ToolResult.fail("date_tool", "Operation 'add_days' requires 'start_date' parameter.")
        if days is None:
            return ToolResult.fail("date_tool", "Operation 'add_days' requires integer 'days' parameter.")

        dt_start = _parse_iso_date(start_date)
        if dt_start is None:
            return ToolResult.fail(
                "date_tool",
                f"Invalid 'start_date' format: '{start_date}'. Must be valid ISO format 'YYYY-MM-DD'.",
                metadata={"start_date": start_date}
            )

        target_dt = dt_start + timedelta(days=days)
        return ToolResult.ok(
            "date_tool",
            data={
                "operation": "add_days",
                "start_date": dt_start.strftime("%Y-%m-%d"),
                "days_added": days,
                "resulting_date": target_dt.strftime("%Y-%m-%d")
            }
        )

    # 4. Subtract days operation
    elif op in ("subtract_days", "subtract"):
        if not start_date:
            return ToolResult.fail("date_tool", "Operation 'subtract_days' requires 'start_date' parameter.")
        if days is None:
            return ToolResult.fail("date_tool", "Operation 'subtract_days' requires integer 'days' parameter.")

        dt_start = _parse_iso_date(start_date)
        if dt_start is None:
            return ToolResult.fail(
                "date_tool",
                f"Invalid 'start_date' format: '{start_date}'. Must be valid ISO format 'YYYY-MM-DD'.",
                metadata={"start_date": start_date}
            )

        target_dt = dt_start - timedelta(days=days)
        return ToolResult.ok(
            "date_tool",
            data={
                "operation": "subtract_days",
                "start_date": dt_start.strftime("%Y-%m-%d"),
                "days_subtracted": days,
                "resulting_date": target_dt.strftime("%Y-%m-%d")
            }
        )

    else:
        return ToolResult.fail(
            "date_tool",
            f"Unsupported date operation '{operation}'. Supported operations: 'current_date', 'current_datetime', 'date_diff', 'add_days', 'subtract_days'.",
            metadata={"operation": operation}
        )


DATE_DEFINITION = ToolDefinition(
    name="date_tool",
    description="Performs calendar operations: gets current date/time, computes date differences, adds/subtracts days with strict ISO 8601 parsing.",
    parameters={
        "operation": ToolParameter(
            name="operation",
            type="string",
            description="Date operation: 'current_date', 'current_datetime', 'date_diff', 'add_days', 'subtract_days'.",
            required=True,
            enum=["current_date", "current_datetime", "date_diff", "add_days", "subtract_days"]
        ),
        "start_date": ToolParameter(
            name="start_date",
            type="string",
            description="Base or starting date in ISO format (YYYY-MM-DD).",
            required=False
        ),
        "end_date": ToolParameter(
            name="end_date",
            type="string",
            description="Ending date in ISO format (YYYY-MM-DD) for 'date_diff'.",
            required=False
        ),
        "days": ToolParameter(
            name="days",
            type="integer",
            description="Number of days to add or subtract.",
            required=False
        ),
        "tz_name": ToolParameter(
            name="tz_name",
            type="string",
            description="Timezone standard name (default 'UTC').",
            required=False,
            default="UTC"
        )
    },
    returns={
        "type": "object",
        "properties": {
            "operation": {"type": "string"},
            "result": {"type": "string"}
        }
    },
    is_mock=False
)
