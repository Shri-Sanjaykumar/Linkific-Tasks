# Error Handling Notes

## 1. Architectural Philosophy

Defensive error handling in production AI systems requires that:
1. **Zero Unhandled Crashes:** No user input, invalid query, or missing file should cause an uncaught traceback or server crash.
2. **Standardized Error Envelopes:** All errors return a uniform `ToolResult(success=False, error=..., metadata=...)` payload.
3. **Actionable Diagnostics:** Error messages must specify exactly what went wrong (e.g. missing required parameter, path not found, division by zero) without exposing private system internals or credentials.
4. **Fail-Fast Tool Chaining:** Pipelines abort on early-stage failures to prevent invalid data pollution in downstream operations.

---

## 2. Exhaustive Error Handling Taxonomy

| Failure Scenario | Guard Mechanism & Implementation | Error Response / Diagnostic Code |
| :--- | :--- | :--- |
| **Invalid User Input** | Type and range validation in tool entrypoints. | `ToolResult.fail("Parameter 'a' must be a numeric value, got str.")` |
| **Missing Required Parameters** | `ToolRegistry.validate_arguments()` verifies required parameter presence before execution. | `Argument validation failed: Missing required parameter 'recipient'.` |
| **Unsupported Tool Requests** | `FunctionCallingEngine.select_tool()` classifies out-of-domain requests as `None`. | `unsupported_request`: "I cannot fulfill this request because no registered tool matches..." |
| **Missing Files** | `file_reader` checks `os.path.exists()` and local `data/` directory fallbacks. | `FILE_NOT_FOUND`: `File not found: 'data/does_not_exist.txt'. Please check path.` |
| **Invalid File Formats** | `file_reader` checks against whitelist `{.txt, .csv, .json, .md}`. | `UNSUPPORTED_FORMAT`: `Unsupported file format '.db'. Allowed: ['.csv', '.json', ...]` |
| **Database Connection Failures** | Traps connection errors and supports `simulate_connection_failure=True`. | `DB_CONNECTION_ERROR`: `Database connection failed: operational timeout or host unreachable.` |
| **Invalid Database Queries** | Traps `sqlite3.OperationalError` for bad syntax or missing tables. | `SQLITE_OPERATIONAL_ERROR`: `SQLite OperationalError: no such table: non_existent_table` |
| **Destructive Database Queries** | Blocks `DROP`, `TRUNCATE`, `DELETE`, `ALTER` via keyword inspection. | `DESTRUCTIVE_QUERY_PROHIBITED`: `Security restriction: Destructive SQL query ('DROP') prohibited.` |
| **Web Search Service Failures** | Simulates upstream timeouts (HTTP 503) via `simulate_service_failure=True`. | `UPSTREAM_SERVICE_TIMEOUT`: `Upstream search provider timeout (HTTP 503 Service Unavailable).` |
| **Weather Service Failures** | Simulates upstream gateway timeouts (HTTP 504) and rejects invalid/numeric locations. | `WEATHER_GATEWAY_TIMEOUT`: `Weather service connection timed out (HTTP 504 Gateway Timeout).` |
| **Invalid Email Addresses** | Verifies recipient against standard RFC-compliant regex pattern. | `INVALID_EMAIL_SYNTAX`: `Invalid recipient email address format: 'not-an-email'.` |
| **Invalid Dates** | `date_tool` uses strict ISO parsing (`%Y-%m-%d`), detecting non-existent leap days. | `INVALID_DATE`: `Invalid 'start_date' format: '2026-02-29'. Must be valid ISO format.` |
| **Empty Datasets** | `data_analyzer` detects empty strings or zero-length record lists. | `EMPTY_DATASET`: `Dataset contains zero rows / records.` |
| **Malformed Datasets** | `data_analyzer` handles non-numeric values in numeric columns and missing target columns. | `Column 'profit_margin' not found in dataset. Available columns: [...]` |
| **Tool Execution Exceptions** | `ToolRegistry.execute()` wraps execution in `try / except Exception as e`. | `Execution error in '<tool_name>': <error details>` |
| **Tool-Chaining Failures** | `ToolChainPipeline` validates Step 1 output before initiating Step 2. | `Step 1 (<tool_name>) failed: <upstream error message>` |

---

## 3. Real Verification Results

Every single one of these 16 defensive scenarios has been implemented in code and verified with real automated PyTest tests:
- Calculator zero-division handled: `PASSED`
- Path traversal blocked & missing files handled: `PASSED`
- SQLite syntax & connection failures handled: `PASSED`
- Email syntax validation & rejection: `PASSED`
- Invalid calendar dates (2026-02-29) handled: `PASSED`
- Chain failure propagation handled: `PASSED`
