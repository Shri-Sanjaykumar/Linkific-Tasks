"""
Day 20 — Function Calling Engine
Implements tool selection, argument extraction/validation, safe execution,
operational tracing, and graceful handling of unsupported requests.
"""

import time
import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple, List
from .schemas import (
    FunctionCallRequest,
    FunctionCallResult,
    ToolResult,
    ExecutionTrace,
    TraceStep
)
from .registry import ToolRegistry, default_registry
from .tools import register_all_tools


class FunctionCallingEngine:
    """Core function-calling engine managing tool selection, validation, and tracing."""

    def __init__(self, registry: Optional[ToolRegistry] = None):
        self.registry = registry or default_registry
        # Ensure standard tools are registered
        if not self.registry.list_tools():
            register_all_tools(self.registry)

    def select_tool(self, user_request: str) -> Tuple[Optional[str], str, Dict[str, Any]]:
        """
        Analyzes user request and selects the appropriate tool.
        Returns (tool_name, selection_reason, extracted_arguments).
        If request is unsupported/out-of-domain, returns (None, reason, {}).
        """
        req_clean = user_request.strip()
        req_lower = req_clean.lower()

        # 1. Date & Time patterns (checked first to prevent ISO dates like 2026-09-01 from matching math subtraction)
        if (("days" in req_lower and "between" in req_lower) or 
            any(w in req_lower for w in ["how many days", "days between", "date difference", "difference between dates"])):
            dates = re.findall(r"\b\d{4}-\d{2}-\d{2}\b", req_clean)
            if len(dates) >= 2:
                return (
                    "date_tool",
                    f"Identified date difference calculation between {dates[0]} and {dates[1]}.",
                    {"operation": "date_diff", "start_date": dates[0], "end_date": dates[1]}
                )
        if any(w in req_lower for w in ["current date", "today's date", "what is today's date", "what day is it"]):
            return (
                "date_tool",
                "Identified request for current calendar date.",
                {"operation": "current_date"}
            )
        if any(w in req_lower for w in ["current time", "current datetime", "what time is it"]):
            return (
                "date_tool",
                "Identified request for current ISO datetime timestamp.",
                {"operation": "current_datetime"}
            )
        if "add" in req_lower and "days to" in req_lower:
            days_m = re.search(r"add\s+(\d+)\s+days to\s+(\d{4}-\d{2}-\d{2})", req_lower)
            if days_m:
                return (
                    "date_tool",
                    f"Identified date addition: adding {days_m.group(1)} days to {days_m.group(2)}.",
                    {"operation": "add_days", "start_date": days_m.group(2), "days": int(days_m.group(1))}
                )

        # 2. Calculator patterns (ignore if text contains ISO dates YYYY-MM-DD)
        if not re.search(r"\b\d{4}-\d{2}-\d{2}\b", req_clean):
            calc_patterns = [
                (r"(?:calculate|compute)?\s*(\d+(?:\.\d+)?)\s*(?:divided by|\/)\s*(\d+(?:\.\d+)?)", "divide"),
                (r"(?:calculate|compute|divide)\s+(\d+(?:\.\d+)?)\s*(?:by|over)\s*(\d+(?:\.\d+)?)", "divide"),
                (r"(?:calculate|compute)?\s*(\d+(?:\.\d+)?)\s*(?:multiplied by|\*|times)\s*(\d+(?:\.\d+)?)", "multiply"),
                (r"(?:calculate|compute|multiply)\s+(\d+(?:\.\d+)?)\s*(?:by|and)\s*(\d+(?:\.\d+)?)", "multiply"),
                (r"(?:calculate|compute)?\s*(\d+(?:\.\d+)?)\s*(?:plus|\+)\s*(\d+(?:\.\d+)?)", "add"),
                (r"(?:calculate|compute|add|sum)\s+(\d+(?:\.\d+)?)\s*(?:and|plus)\s*(\d+(?:\.\d+)?)", "add"),
                (r"(?:calculate|compute)?\s*(\d+(?:\.\d+)?)\s*(?:minus|\-)\s*(\d+(?:\.\d+)?)", "subtract"),
                (r"(?:calculate|compute|subtract)\s+(\d+(?:\.\d+)?)\s*(?:from|minus)\s*(\d+(?:\.\d+)?)", "subtract"),
                (r"(\d+(?:\.\d+)?)\s*([\+\*\/])\s*(\d+(?:\.\d+)?)", None)
            ]
            for pat, op_type in calc_patterns:
                m = re.search(pat, req_lower)
                if m:
                    if op_type is None:
                        sym = m.group(2)
                        op_map = {"+": "add", "*": "multiply", "/": "divide"}
                        op_type = op_map.get(sym, "add")
                        a_val, b_val = float(m.group(1)), float(m.group(3))
                    else:
                        a_val, b_val = float(m.group(1)), float(m.group(2))
                    return (
                        "calculator",
                        f"Identified arithmetic request with operator '{op_type}' and operands {a_val}, {b_val}.",
                        {"a": a_val, "b": b_val, "operation": op_type}
                    )

        # 3. Weather patterns
        if any(w in req_lower for w in ["weather", "temperature", "forecast", "climate", "humidity in", "how cold in", "how hot in"]):
            # Extract city name using word boundaries to prevent matching suffixes of words like 'what'
            city = None
            city_m = re.search(r"\b(?:in|for|at|of)\s+([a-zA-Z\s]+?)(?:\?|$|\.|\s+today|\s+now)", req_clean, re.IGNORECASE)
            if city_m:
                city = city_m.group(1).strip()
            else:
                city_m2 = re.search(r"(?:weather|forecast|temperature)\s+(?:in\s+|for\s+|at\s+)?([a-zA-Z\s]+?)(?:\?|$|\.|\s+today)", req_clean, re.IGNORECASE)
                if city_m2:
                    city = city_m2.group(1).strip()

            if city:
                city = re.sub(r"^(?:is\s+|the\s+|current\s+|weather\s+|in\s+)+", "", city, flags=re.IGNORECASE).strip()
            if not city:
                city = "Bengaluru"

            units = "fahrenheit" if "fahrenheit" in req_lower else "celsius"
            return (
                "weather_tool",
                f"Identified meteorological inquiry targeting location '{city}'.",
                {"location": city, "units": units}
            )

        # 4. Email patterns
        if any(w in req_lower for w in ["email", "send email", "draft email", "mail to"]):
            recip_m = re.search(r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b", req_clean)
            recip = recip_m.group(0) if recip_m else "recipient@linkific.internal"
            act = "simulate_send" if "send" in req_lower else ("draft" if "draft" in req_lower else "validate")
            subj_m = re.search(r"subject\s+[:\-]?\s*['\"]?([^'\"\n]+)['\"]?", req_clean, re.IGNORECASE)
            subj = subj_m.group(1).strip() if subj_m else "Status Notification"
            return (
                "email_tool",
                f"Identified email operation '{act}' for recipient '{recip}'.",
                {"recipient": recip, "subject": subj, "body": "Generated status update from automated function call.", "action": act}
            )

        # 5. Database patterns
        if any(w in req_lower for w in ["database", "sqlite", "table", "sql query", "from employees", "from projects"]):
            if "schema" in req_lower:
                tbl_m = re.search(r"table\s+([a-zA-Z0-9_]+)", req_lower)
                tbl = tbl_m.group(1) if tbl_m else None
                return (
                    "database_tool",
                    "Identified database schema inspection request.",
                    {"operation": "get_schema", "table_name": tbl}
                )
            if "all employees" in req_lower or "read employees" in req_lower:
                return (
                    "database_tool",
                    "Identified table read operation for 'employees'.",
                    {"operation": "read_table", "table_name": "employees"}
                )
            # Custom query detection
            sql_m = re.search(r"(select\s+.+?\s+from\s+.+)", req_clean, re.IGNORECASE)
            if sql_m:
                return (
                    "database_tool",
                    "Identified explicit SQL SELECT statement to execute against local company database.",
                    {"operation": "query", "query": sql_m.group(1)}
                )
            if "salary greater than" in req_lower:
                num_m = re.search(r"greater than\s+(\d+)", req_lower)
                threshold = int(num_m.group(1)) if num_m else 100000
                return (
                    "database_tool",
                    f"Identified employee salary filter query for salaries > {threshold}.",
                    {"operation": "query", "query": "SELECT * FROM employees WHERE salary > ?", "params": [threshold]}
                )

        # 6. Company Search / Policy patterns
        if any(w in req_lower for w in ["company policy", "leave entitlement", "core hours", "linkific policy", "remote work allowance", "onboarding document", "policy guideline"]):
            return (
                "company_search",
                "Identified inquiry regarding Linkific organizational policies and guidelines.",
                {"query": req_clean, "top_k": 3}
            )

        # 7. Data Analyzer patterns
        if any(w in req_lower for w in ["average", "mean", "summary statistics", "min and max", "missing values", "null count", "row count"]) and any(w in req_lower for w in ["csv", "data", "sales", "revenue", "dataset"]):
            file_target = None
            if "sales" in req_lower or "sample_sales" in req_lower:
                file_target = "sample_sales.csv"
            elif "malformed" in req_lower:
                file_target = "malformed.csv"

            op = "summary"
            col = None
            if "average" in req_lower or "mean" in req_lower:
                op = "average"
                col_m = re.search(r"(?:average|mean)\s+(?:of\s+)?([a-zA-Z0-9_]+)", req_lower)
                col = col_m.group(1) if col_m else "revenue"
            elif "row count" in req_lower:
                op = "row_count"
            elif "missing" in req_lower or "null" in req_lower:
                op = "missing_values"

            return (
                "data_analyzer",
                f"Identified tabular data analysis operation '{op}' targeting dataset '{file_target}'.",
                {"operation": op, "file_path": file_target, "target_column": col}
            )

        # 8. PDF Reader patterns
        if ".pdf" in req_lower or any(w in req_lower for w in ["pdf reader", "read pdf", "inspect pdf", "company_handbook", "extract pdf"]):
            path_m = re.search(r"([a-zA-Z0-9_\-\/\\]+\.pdf)", req_clean, re.IGNORECASE)
            pdf_path = path_m.group(1) if path_m else "company_handbook.pdf"
            page_m = re.search(r"page\s+(\d+)", req_lower)
            page_num = int(page_m.group(1)) if page_m else None
            return (
                "pdf_reader",
                f"Identified PDF inspection request targeting '{pdf_path}'.",
                {"file_path": pdf_path, "page_number": page_num}
            )

        # 9. File Reader patterns
        if any(w in req_lower for w in ["read file", "inspect file", "read the contents", "open file", "file_reader"]) or any(ext in req_lower for ext in [".csv", ".txt", ".json", ".md"]):
            path_m = re.search(r"([a-zA-Z0-9_\-\/\\]+\.(?:txt|json|csv|md))", req_clean)
            target_path = path_m.group(1) if path_m else "sample_sales.csv"
            return (
                "file_reader",
                f"Identified file inspection request targeting '{target_path}'.",
                {"file_path": target_path}
            )

        # 9. Web Search patterns
        if any(w in req_lower for w in ["search for", "look up online", "web search", "google", "documentation on"]):
            q_clean = re.sub(r"^(?:search for|look up online|web search for|search)\s+", "", req_clean, flags=re.IGNORECASE).strip()
            return (
                "web_search",
                f"Identified external information lookup request for '{q_clean}'.",
                {"query": q_clean}
            )

        # 10. Out-of-Domain / Unsupported requests
        return (
            None,
            "Request falls outside the operational scope of registered tools. Refusing execution gracefully without hallucinating or selecting unrelated tools.",
            {}
        )

    def execute_request(self, request: FunctionCallRequest) -> Tuple[FunctionCallResult, ExecutionTrace]:
        """
        Executes an end-to-end function calling lifecycle with operational tracing:
        1. Tool Selection
        2. Argument Extraction & Validation
        3. Function Execution
        4. Structured Output Packaging
        """
        start_time = time.time()
        trace_steps = []
        user_req = request.user_request

        # Step 1: Tool Selection
        step1_start = time.time()
        if request.forced_tool:
            selected_tool = request.forced_tool
            reason = f"Explicitly forced tool invocation: '{selected_tool}'."
            arguments = request.context.copy()
        else:
            selected_tool, reason, extracted_args = self.select_tool(user_req)
            arguments = {**extracted_args, **request.context}

        step1_dur = (time.time() - step1_start) * 1000
        trace_steps.append(TraceStep(
            step_name="tool_selection",
            status="ok" if selected_tool else "refused",
            details={
                "selected_tool": selected_tool,
                "reason": reason,
                "arguments_detected": list(arguments.keys())
            },
            duration_ms=round(step1_dur, 2)
        ))

        # Handle unsupported request
        if not selected_tool:
            total_dur = (time.time() - start_time) * 1000
            res = FunctionCallResult(
                user_request=user_req,
                selected_tool=None,
                selection_reason=reason,
                arguments={},
                validation_passed=False,
                validation_errors=["No matching or authorized tool for the given user request."],
                tool_result=ToolResult.fail(
                    tool_name="unsupported",
                    error="I cannot fulfill this request because no registered tool matches the requested capability.",
                    metadata={"reason": reason}
                ),
                execution_time_ms=round(total_dur, 2),
                status="unsupported_request"
            )
            trace = ExecutionTrace(
                timestamp=datetime.now(timezone.utc).isoformat(),
                user_request=user_req,
                selected_tool=None,
                steps=trace_steps,
                final_status="refused",
                total_duration_ms=round(total_dur, 2),
                summary="Request safely refused due to absence of appropriate tool capability."
            )
            return res, trace

        # Step 2: Argument Validation
        step2_start = time.time()
        is_valid, val_errors = self.registry.validate_arguments(selected_tool, arguments)
        step2_dur = (time.time() - step2_start) * 1000
        trace_steps.append(TraceStep(
            step_name="argument_validation",
            status="ok" if is_valid else "error",
            details={
                "validation_passed": is_valid,
                "errors": val_errors,
                "validated_arguments": arguments
            },
            duration_ms=round(step2_dur, 2)
        ))

        if not is_valid:
            total_dur = (time.time() - start_time) * 1000
            res = FunctionCallResult(
                user_request=user_req,
                selected_tool=selected_tool,
                selection_reason=reason,
                arguments=arguments,
                validation_passed=False,
                validation_errors=val_errors,
                tool_result=ToolResult.fail(
                    tool_name=selected_tool,
                    error=f"Parameter validation failed: {'; '.join(val_errors)}",
                    metadata={"validation_errors": val_errors}
                ),
                execution_time_ms=round(total_dur, 2),
                status="validation_error"
            )
            trace = ExecutionTrace(
                timestamp=datetime.now(timezone.utc).isoformat(),
                user_request=user_req,
                selected_tool=selected_tool,
                steps=trace_steps,
                final_status="validation_failed",
                total_duration_ms=round(total_dur, 2),
                summary=f"Argument validation failed for tool '{selected_tool}'."
            )
            return res, trace

        # Step 3: Tool Execution
        step3_start = time.time()
        tool_res = self.registry.execute(selected_tool, arguments)
        step3_dur = (time.time() - step3_start) * 1000
        trace_steps.append(TraceStep(
            step_name="tool_execution",
            status="ok" if tool_res.success else "error",
            details={
                "tool_success": tool_res.success,
                "error": tool_res.error,
                "data_summary": type(tool_res.data).__name__ if tool_res.data is not None else None
            },
            duration_ms=round(step3_dur, 2)
        ))

        total_dur = (time.time() - start_time) * 1000
        status_str = "success" if tool_res.success else "execution_error"

        call_result = FunctionCallResult(
            user_request=user_req,
            selected_tool=selected_tool,
            selection_reason=reason,
            arguments=arguments,
            validation_passed=True,
            validation_errors=[],
            tool_result=tool_res,
            execution_time_ms=round(total_dur, 2),
            status=status_str
        )

        exec_trace = ExecutionTrace(
            timestamp=datetime.now(timezone.utc).isoformat(),
            user_request=user_req,
            selected_tool=selected_tool,
            steps=trace_steps,
            final_status="completed" if tool_res.success else "failed",
            total_duration_ms=round(total_dur, 2),
            summary=f"Tool '{selected_tool}' executed with status '{status_str}'."
        )

        return call_result, exec_trace
