"""
Day 20 — Command-Line Runner & Demonstration Harness
Executes single tool invocations, function calling engine,
multi-tool chaining pipelines, decision matrix validation, and interactive CLI.
"""

import sys
import os
import argparse
import json
import time

# Ensure project root is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from app import (
    FunctionCallingEngine,
    ToolChainPipeline,
    FunctionCallRequest,
    default_registry,
    register_all_tools
)
from app.utils import (
    format_execution_trace_markdown,
    format_chain_result_markdown,
    save_json_file
)


# Standard 10 Decision Matrix Requests
DECISION_MATRIX_REQUESTS = [
    {
        "request_id": "REQ-01",
        "user_request": "Calculate 450 divided by 15",
        "expected_tool": "calculator",
        "required_input": "a=450, b=15, operation='divide'",
        "expected_output": "30",
        "reason_for_selection": "Direct arithmetic request matching division pattern.",
        "tool_chaining_required": False,
        "error_notes": "Division-by-zero handled defensively if b=0."
    },
    {
        "request_id": "REQ-02",
        "user_request": "Search for latest documentation on LangGraph multi-actor workflows",
        "expected_tool": "web_search",
        "required_input": "query='LangGraph multi-actor workflows'",
        "expected_output": "Curated documentation links and snippets",
        "reason_for_selection": "Informational inquiry requiring web/documentation lookup.",
        "tool_chaining_required": False,
        "error_notes": "Demonstration local index; clearly labeled mock notice."
    },
    {
        "request_id": "REQ-03",
        "user_request": "Query employees with salary greater than 100000 from the company database",
        "expected_tool": "database_tool",
        "required_input": "operation='query', query='SELECT * FROM employees WHERE salary > ?', params=[100000]",
        "expected_output": "List of employee records exceeding salary threshold",
        "reason_for_selection": "Structured SQL query filtering SQLite table records.",
        "tool_chaining_required": False,
        "error_notes": "Enforces read-only statements; rejects destructive SQL."
    },
    {
        "request_id": "REQ-04",
        "user_request": "Read and inspect the contents of sample_sales.csv",
        "expected_tool": "file_reader",
        "required_input": "file_path='Day-20/data/sample_sales.csv'",
        "expected_output": "Structured file metadata, character count, and raw content",
        "reason_for_selection": "Direct file inspection on supported local CSV file.",
        "tool_chaining_required": False,
        "error_notes": "Verifies file existence and blocks workspace path traversal."
    },
    {
        "request_id": "REQ-05",
        "user_request": "What is the current weather and temperature in Bengaluru?",
        "expected_tool": "weather_tool",
        "required_input": "location='Bengaluru', units='celsius'",
        "expected_output": "Observation dict with temperature (24.5°C), humidity, and condition",
        "reason_for_selection": "City meteorological lookup request.",
        "tool_chaining_required": False,
        "error_notes": "Demonstration weather database; rejects empty or numeric locations."
    },
    {
        "request_id": "REQ-06",
        "user_request": "Draft an email to mentor@linkific.internal with subject Status Report",
        "expected_tool": "email_tool",
        "required_input": "recipient='mentor@linkific.internal', subject='Status Report', body='...', action='draft'",
        "expected_output": "Draft object with draft_id and status 'draft_saved'",
        "reason_for_selection": "Email composition and syntax validation request.",
        "tool_chaining_required": False,
        "error_notes": "Simulated local drafting; zero real SMTP transmission."
    },
    {
        "request_id": "REQ-07",
        "user_request": "How many days are between 2026-09-01 and 2026-09-22?",
        "expected_tool": "date_tool",
        "required_input": "operation='date_diff', start_date='2026-09-01', end_date='2026-09-22'",
        "expected_output": "21 days difference",
        "reason_for_selection": "Calendar date math between two ISO 8601 timestamps.",
        "tool_chaining_required": False,
        "error_notes": "Strict ISO 8601 format validation; rejects invalid dates."
    },
    {
        "request_id": "REQ-08",
        "user_request": "Compute the average revenue from sample_sales.csv dataset",
        "expected_tool": "data_analyzer",
        "required_input": "operation='average', file_path='Day-20/data/sample_sales.csv', target_column='revenue'",
        "expected_output": "Average value (5150.0) with sample size and audit metrics",
        "reason_for_selection": "Aggregation request over tabular dataset column.",
        "tool_chaining_required": False,
        "error_notes": "Handles missing columns and non-numeric fields defensively."
    },
    {
        "request_id": "REQ-09",
        "user_request": "Look up Linkific company policy guidelines on leave entitlement and core collaboration hours",
        "expected_tool": "company_search",
        "required_input": "query='leave entitlement and core collaboration hours', top_k=3",
        "expected_output": "Matching organizational policy excerpts with relevance scores",
        "reason_for_selection": "Inquiry regarding Linkific corporate governance and guidelines.",
        "tool_chaining_required": False,
        "error_notes": "Indexes local repository synthetic policies; no external intranet."
    },
    {
        "request_id": "REQ-10",
        "user_request": "Tell me a fairy tale about a magic unicorn dancing on the rainbow clouds",
        "expected_tool": None,
        "required_input": "N/A",
        "expected_output": "Graceful refusal notification (unsupported request)",
        "reason_for_selection": "Out-of-domain request with zero matching registered tools.",
        "tool_chaining_required": False,
        "error_notes": "Refused safely without hallucination or unrelated tool calling."
    }
]


def run_single_tool_demonstrations(engine: FunctionCallingEngine) -> Dict[str, Any]:
    """Executes each tool once to demonstrate valid operational success."""
    print("\n" + "="*80)
    print("SECTION 1: INDIVIDUAL TOOL INVOCATIONS (All 10 Tools)")
    print("="*80)

    results = {}
    sales_path = os.path.join(SCRIPT_DIR, "data", "sample_sales.csv")

    calls = [
        ("calculator", {"a": 48.0, "b": 12.0, "operation": "divide"}),
        ("web_search", {"query": "LangGraph stateful workflow"}),
        ("database_tool", {"operation": "query", "query": "SELECT name, role, salary FROM employees WHERE salary > 100000"}),
        ("file_reader", {"file_path": sales_path}),
        ("weather_tool", {"location": "Bengaluru", "units": "celsius"}),
        ("email_tool", {"recipient": "mentor@linkific.internal", "subject": "Day 20 Submission", "body": "Tool creation and chaining verified.", "action": "draft"}),
        ("date_tool", {"operation": "date_diff", "start_date": "2026-09-01", "end_date": "2026-09-22"}),
        ("data_analyzer", {"operation": "summary", "file_path": sales_path}),
        ("company_search", {"query": "remote work and hardware allowance", "top_k": 2}),
        ("pdf_reader", {"file_path": "company_handbook.pdf", "search_keyword": "Tool Chaining"})
    ]

    for tool_name, args in calls:
        res = engine.registry.execute(tool_name, args)
        print(f"\n[Tool: {tool_name}] Success: {res.success}")
        if res.success:
            sample_data = str(res.data)[:120] + ("..." if len(str(res.data)) > 120 else "")
            print(f"  Output: {sample_data}")
        else:
            print(f"  Error: {res.error}")
        results[tool_name] = res.model_dump()

    return results


def run_error_handling_demonstrations(engine: FunctionCallingEngine) -> Dict[str, Any]:
    """Executes error scenarios to verify robust, non-crashing defensive error handling."""
    print("\n" + "="*80)
    print("SECTION 2: DEFENSIVE ERROR HANDLING SCENARIOS")
    print("="*80)

    error_calls = [
        ("calculator_div_zero", "calculator", {"a": 100, "b": 0, "operation": "divide"}),
        ("calculator_bad_op", "calculator", {"a": 10, "b": 5, "operation": "modulus"}),
        ("web_search_empty", "web_search", {"query": "   "}),
        ("web_search_timeout", "web_search", {"query": "python", "simulate_service_failure": True}),
        ("database_bad_table", "database_tool", {"operation": "query", "query": "SELECT * FROM non_existent_table"}),
        ("database_destructive_block", "database_tool", {"operation": "query", "query": "DROP TABLE employees"}),
        ("database_conn_fail", "database_tool", {"operation": "query", "query": "SELECT 1", "simulate_connection_failure": True}),
        ("file_reader_missing", "file_reader", {"file_path": "data/does_not_exist.txt"}),
        ("file_reader_bad_ext", "file_reader", {"file_path": "data/company_records.db"}),
        ("weather_invalid_city", "weather_tool", {"location": "123456"}),
        ("weather_service_outage", "weather_tool", {"location": "Bengaluru", "simulate_service_failure": True}),
        ("email_invalid_syntax", "email_tool", {"recipient": "not-an-email", "subject": "Hi", "body": "Test"}),
        ("date_invalid_leap", "date_tool", {"operation": "date_diff", "start_date": "2026-02-29", "end_date": "2026-03-01"}),
        ("data_analyzer_empty", "data_analyzer", {"data": "  ", "operation": "summary"}),
        ("data_analyzer_missing_col", "data_analyzer", {"file_path": os.path.join(SCRIPT_DIR, "data", "sample_sales.csv"), "operation": "average", "target_column": "profit_margin"}),
        ("unsupported_tool", "non_existent_tool", {"dummy": 123})
    ]

    error_results = {}
    for label, tool_name, args in error_calls:
        res = engine.registry.execute(tool_name, args)
        print(f"\n[Scenario: {label}] (Tool: {tool_name})")
        print(f"  Handled Gracefully: {not res.success}")
        print(f"  Error Message: {res.error}")
        error_results[label] = res.model_dump()

    return error_results


def run_tool_chaining_demonstrations(pipeline: ToolChainPipeline) -> Dict[str, Any]:
    """Executes and logs all 3 tool-chaining pipelines."""
    print("\n" + "="*80)
    print("SECTION 3: TOOL CHAINING WORKFLOW DEMONSTRATIONS (3 Concrete Pipelines)")
    print("="*80)

    chains_output = {}
    sales_path = os.path.join(SCRIPT_DIR, "data", "sample_sales.csv")

    # Chain 1: File Reader -> Data Analyzer
    print("\nExecuting Chain 1: File Reader -> Data Analyzer")
    c1 = pipeline.chain_file_to_analyzer(file_path=sales_path, analysis_operation="summary")
    print(f"  Success: {c1.success} (Duration: {c1.total_duration_ms:.2f} ms)")
    if c1.success:
        cols = c1.final_output.get("columns", [])
        rows = c1.final_output.get("total_rows")
        print(f"  Result: Successfully analyzed {rows} rows across columns {cols}")
    chains_output["chain_1_file_to_analyzer"] = c1.model_dump()

    # Chain 2: Database Tool -> Data Analyzer
    print("\nExecuting Chain 2: Database Tool -> Data Analyzer")
    c2 = pipeline.chain_database_to_analyzer(
        query="SELECT salary, tenure_years FROM employees;",
        analysis_operation="average",
        target_column="salary"
    )
    print(f"  Success: {c2.success} (Duration: {c2.total_duration_ms:.2f} ms)")
    if c2.success:
        avg_sal = c2.final_output.get("average")
        size = c2.final_output.get("sample_size")
        print(f"  Result: Computed average employee salary: ${avg_sal:,.2f} across {size} employees")
    chains_output["chain_2_database_to_analyzer"] = c2.model_dump()

    # Chain 3: Date Tool -> Calculator
    print("\nExecuting Chain 3: Date Tool -> Calculator")
    c3 = pipeline.chain_date_to_calculator(
        start_date="2026-09-01",
        end_date="2026-09-22",
        multiplier=8.0,
        operation="multiply"
    )
    print(f"  Success: {c3.success} (Duration: {c3.total_duration_ms:.2f} ms)")
    if c3.success:
        days = c3.final_output.get("interval_days")
        hrs = c3.final_output.get("calculated_total")
        print(f"  Result: {days} days * 8.0 hours/day = {hrs} total working hours")
    chains_output["chain_3_date_to_calculator"] = c3.model_dump()

    return chains_output


def run_decision_matrix_demonstration(engine: FunctionCallingEngine) -> List[Dict[str, Any]]:
    """Executes all 10 Decision Matrix requests and records structured outcomes."""
    print("\n" + "="*80)
    print("SECTION 4: FUNCTION CALLING DECISION MATRIX (10 Real-World Requests)")
    print("="*80)

    matrix_results = []
    trace_markdowns = []

    for req in DECISION_MATRIX_REQUESTS:
        rid = req["request_id"]
        query = req["user_request"]
        print(f"\n[{rid}] Query: \"{query}\"")

        call_req = FunctionCallRequest(user_request=query)
        result, trace = engine.execute_request(call_req)

        print(f"  Selected Tool: {result.selected_tool}")
        print(f"  Status: {result.status}")
        print(f"  Duration: {result.execution_time_ms:.2f} ms")
        if result.tool_result:
            if result.tool_result.success:
                sample_out = str(result.tool_result.data)[:100]
                print(f"  Result: {sample_out}...")
            else:
                print(f"  Notice/Error: {result.tool_result.error}")

        record = {
            "request_id": rid,
            "user_request": query,
            "selected_tool": result.selected_tool,
            "arguments": result.arguments,
            "validation_passed": result.validation_passed,
            "status": result.status,
            "reason_for_selection": req["reason_for_selection"],
            "tool_chaining_required": req["tool_chaining_required"],
            "error_notes": req["error_notes"],
            "result_success": result.tool_result.success if result.tool_result else False,
            "trace_id": trace.trace_id,
            "execution_time_ms": result.execution_time_ms
        }
        matrix_results.append(record)
        trace_markdowns.append(format_execution_trace_markdown(trace))

    # Save traces to outputs/execution_trace.md
    traces_file = os.path.join(SCRIPT_DIR, "outputs", "execution_trace.md")
    os.makedirs(os.path.dirname(traces_file), exist_ok=True)
    with open(traces_file, "w", encoding="utf-8") as f:
        f.write("# Day 20 — Function Calling Execution Traces\n\n")
        f.write("\n\n---\n\n".join(trace_markdowns))
    print(f"\nSaved execution traces to: {traces_file}")

    return matrix_results


def run_interactive_mode(engine: FunctionCallingEngine):
    """Provides interactive terminal session for asking random questions and testing function calling."""
    print("\n" + "="*80)
    print("LINKIFIC AI/ML INTERNSHIP — DAY 20: FUNCTION CALLING CLI")
    print("="*80)
    print("Ask any question or request a calculation, weather, database query, file reading, etc.")
    print("Commands to exit: 'exit', 'quit', 'q'\n")

    while True:
        try:
            user_input = input("\nEnter request: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSession ended safely.")
            break

        if not user_input:
            print("Please enter a non-empty request.")
            continue

        if user_input.lower() in ("exit", "quit", "q"):
            print("Session ended safely. Goodbye!")
            break

        call_req = FunctionCallRequest(user_request=user_input)
        res, trace = engine.execute_request(call_req)

        print("\n--- FUNCTION CALL OUTCOME ---")
        print(f"Selected Tool: {res.selected_tool or 'None (Refused)'}")
        print(f"Reason: {res.selection_reason}")
        print(f"Status: {res.status} ({res.execution_time_ms:.2f} ms)")
        if res.tool_result:
            if res.tool_result.success:
                print(f"Data: {json.dumps(res.tool_result.data, indent=2, default=str)}")
            else:
                print(f"Error: {res.tool_result.error}")
        print("-----------------------------\n")


def main():
    parser = argparse.ArgumentParser(description="Day 20 — Function Calling & Tool Chaining Runner")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive function-calling CLI")
    parser.add_argument("--tools", action="store_true", help="Run individual tool demonstrations")
    parser.add_argument("--chains", action="store_true", help="Run tool-chaining demonstrations")
    parser.add_argument("--errors", action="store_true", help="Run error-handling scenarios")
    parser.add_argument("--matrix", action="store_true", help="Run 10-request decision matrix")
    parser.add_argument("--all", action="store_true", help="Run all demonstrations and save example outputs (default)")

    args = parser.parse_args()

    engine = FunctionCallingEngine()
    pipeline = ToolChainPipeline()

    if args.interactive:
        run_interactive_mode(engine)
        return

    run_all = args.all or (not args.tools and not args.chains and not args.errors and not args.matrix)

    examples_dir = os.path.join(SCRIPT_DIR, "examples")
    outputs_dir = os.path.join(SCRIPT_DIR, "outputs")
    os.makedirs(examples_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)

    if args.tools or run_all:
        tools_res = run_single_tool_demonstrations(engine)
        save_json_file(tools_res, os.path.join(examples_dir, "single_tool_calls.json"))

    if args.errors or run_all:
        errors_res = run_error_handling_demonstrations(engine)
        save_json_file(errors_res, os.path.join(examples_dir, "error_scenarios.json"))

    if args.chains or run_all:
        chains_res = run_tool_chaining_demonstrations(pipeline)
        save_json_file(chains_res, os.path.join(examples_dir, "tool_chain_execution.json"))

    if args.matrix or run_all:
        matrix_res = run_decision_matrix_demonstration(engine)
        save_json_file(matrix_res, os.path.join(examples_dir, "decision_matrix_results.json"))

    print("\n" + "="*80)
    print("ALL DAY-20 DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
    print("="*80)


if __name__ == "__main__":
    main()
