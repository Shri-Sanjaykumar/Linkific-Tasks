"""
Day 20 — Automated Test Suite for Tool Creation, Function Calling,
Tool Chaining, and Error Handling.
Covers all 16 required test categories across 40+ unit and integration tests.
"""

import os
import sys
import pytest

# Ensure Day-20 directory is on sys.path
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
DAY20_DIR = os.path.dirname(TESTS_DIR)
if DAY20_DIR not in sys.path:
    sys.path.insert(0, DAY20_DIR)

from app import (
    FunctionCallingEngine,
    ToolChainPipeline,
    ToolRegistry,
    FunctionCallRequest,
    ToolResult,
    default_registry,
    register_all_tools
)
from app.tools import (
    calculator_tool,
    web_search_tool,
    database_tool,
    file_reader_tool,
    weather_tool,
    email_tool,
    date_tool,
    data_analyzer_tool,
    company_search_tool,
    pdf_reader_tool
)


@pytest.fixture(scope="module")
def engine():
    reg = ToolRegistry()
    register_all_tools(reg)
    return FunctionCallingEngine(registry=reg)


@pytest.fixture(scope="module")
def pipeline(engine):
    return ToolChainPipeline(registry=engine.registry)


# ==============================================================================
# CATEGORY 1 & 16: Tool Registration & Schema / Registry Validation
# ==============================================================================

def test_tool_registration_all_tools(engine):
    """Verifies all 10 tools (8 standard + 2 company project tools) are registered."""
    tools = engine.registry.list_tools()
    expected = [
        "calculator", "web_search", "database_tool", "file_reader",
        "weather_tool", "email_tool", "date_tool", "data_analyzer", "company_search",
        "pdf_reader"
    ]
    for t in expected:
        assert t in tools, f"Expected tool '{t}' not found in registry."
    assert len(tools) >= 10


def test_tool_schema_export_json(engine):
    """Verifies all registered tools produce valid OpenAI/JSON-schema function definitions."""
    schemas = engine.registry.get_all_schemas()
    assert len(schemas) >= 9
    for s in schemas:
        assert s.get("type") == "function"
        fn = s.get("function", {})
        assert "name" in fn
        assert "description" in fn
        assert "parameters" in fn
        assert fn["parameters"].get("type") == "object"
        assert "properties" in fn["parameters"]


def test_tool_definition_attributes(engine):
    """Verifies metadata properties on registered tool definitions."""
    calc_def = engine.registry.get_definition("calculator")
    assert calc_def is not None
    assert calc_def.name == "calculator"
    assert "operation" in calc_def.parameters
    assert calc_def.is_mock is False

    web_def = engine.registry.get_definition("web_search")
    assert web_def is not None
    assert web_def.is_mock is True
    assert web_def.mock_notice is not None


# ==============================================================================
# CATEGORY 2, 3, 4: Calculator Tool (Valid, Invalid, Division by Zero)
# ==============================================================================

def test_calculator_valid_operations():
    """Tests addition, subtraction, multiplication, and division."""
    res_add = calculator_tool(a=25, b=15, operation="add")
    assert res_add.success is True
    assert res_add.data["result"] == 40

    res_sub = calculator_tool(a=50, b=18, operation="subtract")
    assert res_sub.success is True
    assert res_sub.data["result"] == 32

    res_mul = calculator_tool(a=7, b=8, operation="multiply")
    assert res_mul.success is True
    assert res_mul.data["result"] == 56

    res_div = calculator_tool(a=100, b=4, operation="divide")
    assert res_div.success is True
    assert res_div.data["result"] == 25


def test_calculator_invalid_input():
    """Tests non-numeric operands are rejected defensively."""
    res = calculator_tool(a="invalid_string", b=10, operation="add")
    assert res.success is False
    assert "must be a numeric value" in res.error

    res_bool = calculator_tool(a=True, b=10, operation="add")
    assert res_bool.success is False


def test_calculator_division_by_zero():
    """Tests division by zero returns structured failure without crashing."""
    res = calculator_tool(a=100, b=0, operation="divide")
    assert res.success is False
    assert "Division by zero is not allowed" in res.error
    assert res.metadata.get("operation") == "divide"


def test_calculator_unsupported_operation():
    """Tests unsupported mathematical operation returns error."""
    res = calculator_tool(a=10, b=2, operation="power")
    assert res.success is False
    assert "Unsupported operation" in res.error


# ==============================================================================
# CATEGORY 5: Database Tool (Success & Failure Handling)
# ==============================================================================

def test_database_get_schema():
    """Tests schema inspection of tables in SQLite."""
    res = database_tool(operation="get_schema")
    assert res.success is True
    assert "employees" in res.data["tables"]
    assert "projects" in res.data["tables"]


def test_database_read_table():
    """Tests reading all records from 'projects' table."""
    res = database_tool(operation="read_table", table_name="projects")
    assert res.success is True
    assert res.data["record_count"] >= 4
    first_proj = res.data["records"][0]
    assert "project_id" in first_proj
    assert "budget" in first_proj


def test_database_parameterized_query():
    """Tests parameterized SELECT query execution."""
    res = database_tool(
        operation="query",
        query="SELECT id, name, salary FROM employees WHERE salary > ?",
        params=[100000]
    )
    assert res.success is True
    assert res.data["record_count"] >= 3
    for row in res.data["records"]:
        assert row["salary"] > 100000


def test_database_syntax_error():
    """Tests invalid SQL syntax returns graceful error."""
    res = database_tool(operation="query", query="SELECT * FROM WHERE INVALID SYNTAX")
    assert res.success is False
    assert "SQLite OperationalError" in res.error or "syntax error" in res.error.lower()


def test_database_missing_table():
    """Tests query targeting non-existent table returns error."""
    res = database_tool(operation="read_table", table_name="non_existent_table")
    assert res.success is False
    assert "does not exist" in res.error


def test_database_destructive_query_blocked():
    """Tests security policy blocks destructive SQL operations (DROP, DELETE)."""
    res = database_tool(operation="query", query="DROP TABLE employees;")
    assert res.success is False
    assert "Security restriction" in res.error
    assert "prohibited" in res.error.lower()


def test_database_connection_failure():
    """Tests simulated database connection failure."""
    res = database_tool(operation="query", query="SELECT 1", simulate_connection_failure=True)
    assert res.success is False
    assert "Database connection failed" in res.error


# ==============================================================================
# CATEGORY 6 & 7: File Reader Tool (Success & Missing-File Handling)
# ==============================================================================

def test_file_reader_success_csv():
    """Tests reading valid CSV file with metadata parsing."""
    csv_path = os.path.join(DAY20_DIR, "data", "sample_sales.csv")
    res = file_reader_tool(file_path=csv_path)
    assert res.success is True
    assert res.data["filename"] == "sample_sales.csv"
    assert res.data["extension"] == ".csv"
    assert res.data["char_count"] > 0
    assert res.data["line_count"] > 5
    assert isinstance(res.data["parsed_structure"], list)


def test_file_reader_success_json():
    """Tests reading valid JSON file with parsed structure."""
    json_path = os.path.join(DAY20_DIR, "data", "sample_employees.json")
    res = file_reader_tool(file_path=json_path)
    assert res.success is True
    assert res.data["extension"] == ".json"
    assert isinstance(res.data["parsed_structure"], list)
    assert len(res.data["parsed_structure"]) >= 5


def test_file_reader_missing_file():
    """Tests reading non-existent file returns clean error."""
    res = file_reader_tool(file_path="Day-20/data/ghost_file.txt")
    assert res.success is False
    assert "File not found" in res.error
    assert res.metadata.get("error_code") == "FILE_NOT_FOUND"


def test_file_reader_unsupported_extension():
    """Tests extension whitelisting rejects unsupported file types."""
    db_path = os.path.join(DAY20_DIR, "data", "company_records.db")
    res = file_reader_tool(file_path=db_path)
    assert res.success is False
    assert "Unsupported file format" in res.error
    assert res.metadata.get("error_code") == "UNSUPPORTED_FORMAT"


def test_file_reader_relative_fallback():
    """Tests resolving file by filename inside data directory."""
    res = file_reader_tool(file_path="sample_sales.csv")
    assert res.success is True
    assert res.data["filename"] == "sample_sales.csv"


# ==============================================================================
# CATEGORY 8: Date Tool (Validation & Temporal Math)
# ==============================================================================

def test_date_tool_current_date():
    """Tests current date returns ISO format string."""
    res = date_tool(operation="current_date")
    assert res.success is True
    assert len(res.data["date"]) == 10  # YYYY-MM-DD


def test_date_tool_date_diff():
    """Tests date difference calculation."""
    res = date_tool(operation="date_diff", start_date="2026-09-01", end_date="2026-09-22")
    assert res.success is True
    assert res.data["days_difference"] == 21
    assert res.data["hours_difference"] == 21 * 24


def test_date_tool_add_days():
    """Tests adding days to base date."""
    res = date_tool(operation="add_days", start_date="2026-09-10", days=5)
    assert res.success is True
    assert res.data["resulting_date"] == "2026-09-15"


def test_date_tool_invalid_date_format():
    """Tests invalid date string is rejected defensively."""
    res = date_tool(operation="date_diff", start_date="invalid_date", end_date="2026-09-22")
    assert res.success is False
    assert "Invalid 'start_date' format" in res.error


def test_date_tool_invalid_leap_year():
    """Tests non-existent leap year day (2026-02-29) is rejected."""
    res = date_tool(operation="date_diff", start_date="2026-02-29", end_date="2026-03-01")
    assert res.success is False
    assert "Invalid 'start_date' format" in res.error


# ==============================================================================
# CATEGORY 9: Data Analyzer Tool
# ==============================================================================

def test_data_analyzer_summary_csv():
    """Tests full statistical profiling on sales dataset."""
    csv_path = os.path.join(DAY20_DIR, "data", "sample_sales.csv")
    res = data_analyzer_tool(operation="summary", file_path=csv_path)
    assert res.success is True
    assert res.data["total_rows"] == 10
    assert "column_statistics" in res.data
    assert "revenue" in res.data["column_statistics"]


def test_data_analyzer_row_count():
    """Tests row count calculation."""
    csv_path = os.path.join(DAY20_DIR, "data", "sample_sales.csv")
    res = data_analyzer_tool(operation="row_count", file_path=csv_path)
    assert res.success is True
    assert res.data["row_count"] == 10


def test_data_analyzer_column_info():
    """Tests column name and data type inference."""
    csv_path = os.path.join(DAY20_DIR, "data", "sample_sales.csv")
    res = data_analyzer_tool(operation="column_info", file_path=csv_path)
    assert res.success is True
    assert "revenue" in res.data["columns"]
    assert "units_sold" in res.data["columns"]


def test_data_analyzer_average():
    """Tests mean calculation on numeric column."""
    csv_path = os.path.join(DAY20_DIR, "data", "sample_sales.csv")
    res = data_analyzer_tool(operation="average", file_path=csv_path, target_column="revenue")
    assert res.success is True
    assert res.data["average"] == 4950.0


def test_data_analyzer_min_max():
    """Tests min and max calculation."""
    csv_path = os.path.join(DAY20_DIR, "data", "sample_sales.csv")
    res = data_analyzer_tool(operation="min_max", file_path=csv_path, target_column="revenue")
    assert res.success is True
    assert res.data["minimum"] == 3600.0
    assert res.data["maximum"] == 7200.0


def test_data_analyzer_missing_values():
    """Tests null/missing values audit."""
    csv_path = os.path.join(DAY20_DIR, "data", "sample_sales.csv")
    res = data_analyzer_tool(operation="missing_values", file_path=csv_path)
    assert res.success is True
    assert "missing_audit" in res.data


def test_data_analyzer_missing_column():
    """Tests requesting analysis on non-existent column returns error."""
    csv_path = os.path.join(DAY20_DIR, "data", "sample_sales.csv")
    res = data_analyzer_tool(operation="average", file_path=csv_path, target_column="non_existent_column")
    assert res.success is False
    assert "not found in dataset" in res.error


def test_data_analyzer_empty_dataset():
    """Tests empty dataset string returns clean error."""
    res = data_analyzer_tool(operation="summary", data="   ")
    assert res.success is False
    assert "empty" in res.error.lower()


# ==============================================================================
# CATEGORY 14: Company Project Practical Tool (company_search)
# ==============================================================================

def test_company_search_policy_query():
    """Tests searching Linkific organizational policy documents."""
    res = company_search_tool(query="leave entitlement and core collaboration hours", top_k=2)
    assert res.success is True
    assert res.data["matches_count"] >= 1
    first_match = res.data["matches"][0]
    assert "document_id" in first_match
    assert "relevance_score" in first_match
    assert first_match["relevance_score"] > 0


def test_company_search_empty_query():
    """Tests empty policy search query is rejected."""
    res = company_search_tool(query="   ")
    assert res.success is False
    assert "cannot be empty" in res.error


def test_company_search_category_filter():
    """Tests category filtering on policy documents."""
    res = company_search_tool(query="remote work", category="Corporate Policy")
    assert res.success is True


# ==============================================================================
# CATEGORY 10, 11, 15: Function Calling Engine, Decision Matrix & Tracing
# ==============================================================================

@pytest.mark.parametrize("req_data", [
    ("Calculate 450 divided by 15", "calculator"),
    ("Search for latest documentation on LangGraph multi-actor workflows", "web_search"),
    ("Query employees with salary greater than 100000 from the company database", "database_tool"),
    ("Read and inspect the contents of sample_sales.csv", "file_reader"),
    ("What is the current weather and temperature in Bengaluru?", "weather_tool"),
    ("Draft an email to mentor@linkific.internal with subject Status Report", "email_tool"),
    ("How many days are between 2026-09-01 and 2026-09-22?", "date_tool"),
    ("Compute the average revenue from sample_sales.csv dataset", "data_analyzer"),
    ("Look up Linkific company policy guidelines on leave entitlement and core collaboration hours", "company_search"),
])
def test_engine_decision_matrix_valid_requests(engine, req_data):
    """Verifies tool selection and execution for Decision Matrix requests."""
    query, expected_tool = req_data
    call_req = FunctionCallRequest(user_request=query)
    res, trace = engine.execute_request(call_req)

    assert res.selected_tool == expected_tool, f"Expected {expected_tool}, got {res.selected_tool} for '{query}'"
    assert res.status == "success"
    assert res.tool_result is not None
    assert res.tool_result.success is True
    assert trace.final_status == "completed"


def test_weather_chennai_query(engine):
    """Verifies interactive uppercase query 'WHAT IS WEATHER IN CHENNAI' routes to weather_tool and returns Chennai data."""
    call_req = FunctionCallRequest(user_request="WHAT IS WEATHER IN CHENNAI")
    res, trace = engine.execute_request(call_req)
    assert res.selected_tool == "weather_tool"
    assert res.status == "success"
    assert res.tool_result.success is True
    assert res.tool_result.data["location"] == "Chennai"
    assert isinstance(res.tool_result.data["temperature"], (int, float))
    assert res.tool_result.data["temperature"] > 0


def test_engine_unsupported_request_refusal(engine):
    """REQ-10: Verifies out-of-domain request is refused safely without executing unrelated tools."""
    query = "Tell me a fairy tale about a magic unicorn dancing on the rainbow clouds"
    call_req = FunctionCallRequest(user_request=query)
    res, trace = engine.execute_request(call_req)

    assert res.selected_tool is None
    assert res.status == "unsupported_request"
    assert res.validation_passed is False
    assert trace.final_status == "refused"
    assert "safely refused" in trace.summary.lower()


def test_engine_execution_trace_structure(engine):
    """Verifies operational trace contains structured steps, timing, and concise details."""
    call_req = FunctionCallRequest(user_request="Calculate 100 plus 25")
    res, trace = engine.execute_request(call_req)

    assert trace.trace_id.startswith("TRC-")
    assert len(trace.steps) == 3
    step_names = [s.step_name for s in trace.steps]
    assert step_names == ["tool_selection", "argument_validation", "tool_execution"]
    assert trace.total_duration_ms >= 0


def test_engine_argument_validation_failure(engine):
    """Verifies validation failure produces structured validation_error without crashing."""
    # Force calculator with invalid argument types
    call_req = FunctionCallRequest(
        user_request="Forced bad calculator",
        forced_tool="calculator",
        context={"a": "not_a_number", "b": 10, "operation": "add"}
    )
    res, trace = engine.execute_request(call_req)

    assert res.status == "validation_error"
    assert res.validation_passed is False
    assert len(res.validation_errors) > 0
    assert trace.final_status == "validation_failed"


# ==============================================================================
# CATEGORY 12: Tool Chaining (All 3 Concrete Pipelines)
# ==============================================================================

def test_chain_1_file_reader_to_data_analyzer(pipeline):
    """Verifies Chain 1 (File Reader -> Data Analyzer) end-to-end."""
    sales_path = os.path.join(DAY20_DIR, "data", "sample_sales.csv")
    result = pipeline.chain_file_to_analyzer(file_path=sales_path, analysis_operation="summary")

    assert result.success is True
    assert len(result.steps) == 2
    assert result.steps[0].tool_name == "file_reader"
    assert result.steps[1].tool_name == "data_analyzer"
    assert result.final_output["total_rows"] == 10
    assert "column_statistics" in result.final_output


def test_chain_2_database_to_data_analyzer(pipeline):
    """Verifies Chain 2 (Database Tool -> Data Analyzer) end-to-end."""
    result = pipeline.chain_database_to_analyzer(
        query="SELECT salary, tenure_years FROM employees;",
        analysis_operation="average",
        target_column="salary"
    )

    assert result.success is True
    assert len(result.steps) == 2
    assert result.steps[0].tool_name == "database_tool"
    assert result.steps[1].tool_name == "data_analyzer"
    assert result.final_output["average"] > 100000
    assert result.final_output["sample_size"] == 6


def test_chain_3_date_to_calculator(pipeline):
    """Verifies Chain 3 (Date Tool -> Calculator) end-to-end."""
    result = pipeline.chain_date_to_calculator(
        start_date="2026-09-01",
        end_date="2026-09-22",
        multiplier=8.0,
        operation="multiply"
    )

    assert result.success is True
    assert len(result.steps) == 2
    assert result.steps[0].tool_name == "date_tool"
    assert result.steps[1].tool_name == "calculator"
    assert result.final_output["interval_days"] == 21
    assert result.final_output["calculated_total"] == 168.0


def test_chain_failure_propagation(pipeline):
    """Verifies that failure in an early step stops the chain gracefully."""
    result = pipeline.chain_file_to_analyzer(file_path="Day-20/data/non_existent_file.csv")
    assert result.success is False
    assert len(result.steps) == 1
    assert result.steps[0].status == "failed"
    assert "Step 1 (file_reader) failed" in result.error


# ==============================================================================
# CATEGORY 13: Error Response Structure Validation
# ==============================================================================

def test_error_response_standard_structure():
    """Verifies that all failure envelopes adhere to standard ToolResult schema."""
    res1 = calculator_tool(a=1, b=0, operation="divide")
    assert isinstance(res1, ToolResult)
    assert res1.success is False
    assert res1.data is None
    assert res1.error is not None
    assert isinstance(res1.metadata, dict)

    res2 = file_reader_tool(file_path="does_not_exist.txt")
    assert isinstance(res2, ToolResult)
    assert res2.success is False
    assert res2.error is not None
    assert "error_code" in res2.metadata


# ==============================================================================
# CATEGORY 17: Dynamic Functionality & PDF Reader Tool
# ==============================================================================

def test_email_tool_draft_persistence():
    """Verifies that drafting an email persists genuine .eml and .json files to disk."""
    res = email_tool(
        recipient="mentor@linkific.internal",
        subject="Sprint Review Summary",
        body="Tool creation, dynamic execution, and error handling complete.",
        action="draft"
    )
    assert res.success is True
    assert "draft_id" in res.data
    assert "saved_file" in res.data
    assert os.path.exists(res.data["saved_file"])

    # Verify listing drafts from disk
    list_res = email_tool(recipient="test@linkific.internal", subject="Test", body="Body", action="list_drafts")
    assert list_res.success is True
    assert list_res.data["total_drafts"] >= 1


def test_pdf_reader_handbook():
    """Verifies PDF reader extracts text and metadata dynamically from company_handbook.pdf."""
    res = pdf_reader_tool(file_path="company_handbook.pdf")
    assert res.success is True
    assert res.data["total_pages"] >= 2
    assert "Linkific" in res.data["summary_preview"] or "LINKIFIC" in res.data["summary_preview"]


def test_pdf_reader_keyword_search():
    """Verifies in-document keyword search across pages in PDF."""
    res = pdf_reader_tool(file_path="company_handbook.pdf", search_keyword="Tool Chaining")
    assert res.success is True
    assert res.data["matches_found"] >= 1
    assert res.data["matching_pages"][0]["page"] == 2


def test_pdf_reader_missing_file():
    """Verifies PDF reader error handling on non-existent file."""
    res = pdf_reader_tool(file_path="ghost_handbook.pdf")
    assert res.success is False
    assert "PDF file not found" in res.error
    assert res.metadata.get("error_code") == "FILE_NOT_FOUND"


def test_pdf_reader_unsupported_format():
    """Verifies PDF reader rejects non-PDF file."""
    res = pdf_reader_tool(file_path="sample_sales.csv")
    assert res.success is False
    assert "Invalid file extension" in res.error
    assert res.metadata.get("error_code") == "UNSUPPORTED_FORMAT"

