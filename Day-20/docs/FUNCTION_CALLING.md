# Function Calling Documentation

## 1. Concept and Lifecycle

Function calling enables an AI agent or application workflow to translate unstructured natural language requests into structured tool selections, validated argument payloads, and deterministic API executions.

### Function Calling Lifecycle

```
User Natural Language Request
             │
             ▼
  [1] Intent & Tool Selection  ──(No tool matches)──►  Graceful Refusal (unsupported_request)
             │
      (Tool Identified)
             ▼
  [2] Argument Extraction & Schema Validation  ──(Invalid types/missing args)──► Validation Error Envelope
             │
      (Schema Validated)
             ▼
  [3] Tool Registry Dispatch
             │
             ▼
  [4] Tool Execution & Error Trapping
             │
             ▼
  [5] Envelope Packaging & Execution Tracing
```

---

## 2. Tool Registry Architecture

The `ToolRegistry` (`app.registry`) maintains an active index of registered tools and their JSON schemas.

### Key Capabilities:
1. **Schema Generation:** Converts `ToolDefinition` instances into standard OpenAI-compatible function calling schemas (`to_json_schema()`).
2. **Pre-Execution Argument Validation:**
   - Validates that all required parameters are present in the argument dictionary.
   - Enforces type constraints (`number`, `integer`, `string`, `boolean`, `array`, `object`).
   - Validates argument values against allowed enum values.
3. **Safe Execution Boundary:** Catches runtime exceptions and wraps them in a standardized `ToolResult` envelope (`success=False`, `error=str(e)`).

---

## 3. Tool Selection Logic

The `FunctionCallingEngine.select_tool()` method inspects the semantic intent, keywords, and entity patterns within the user query:

1. **Date & Time vs Arithmetic Isolation:** Because ISO dates (e.g. `2026-09-01`) contain hyphens (`-`), date queries are evaluated before arithmetic patterns to prevent calendar intervals from being parsed as mathematical subtraction.
2. **Entity Extraction:**
   - Numeric operands and arithmetic operations are mapped to `calculator`.
   - City names and units are mapped to `weather_tool`.
   - Calendar intervals, offsets, and ISO dates are mapped to `date_tool`.
   - Email addresses and draft intentions are mapped to `email_tool`.
   - SQL queries and salary filters are mapped to `database_tool`.
   - Tabular metric requests (averages, row counts, summaries) are mapped to `data_analyzer`.
   - File references (`.csv`, `.json`, `.txt`) are mapped to `file_reader`.
   - Technical research topics are mapped to `web_search`.
   - Linkific policy and corporate guideline inquiries are mapped to `company_search`.
3. **Out-of-Domain Guardrail:** Requests outside the scope of registered tools (such as fantasy stories, creative writing, or unsupported general knowledge) are classified as `unsupported_request`. The engine gracefully refuses execution rather than selecting an arbitrary or unrelated tool.

---

## 4. Operational Execution Tracing

To ensure full auditability without leaking internal chain-of-thought, the engine logs an `ExecutionTrace` for every request:

```json
{
  "trace_id": "TRC-8F42A1",
  "timestamp": "2026-09-22T10:30:57.123456Z",
  "user_request": "Calculate 450 divided by 15",
  "selected_tool": "calculator",
  "final_status": "completed",
  "total_duration_ms": 0.33,
  "summary": "Tool 'calculator' executed with status 'success'.",
  "steps": [
    {
      "step_name": "tool_selection",
      "status": "ok",
      "duration_ms": 0.12,
      "details": {
        "selected_tool": "calculator",
        "reason": "Identified arithmetic request with operator 'divide' and operands 450.0, 15.0."
      }
    },
    {
      "step_name": "argument_validation",
      "status": "ok",
      "duration_ms": 0.08,
      "details": {
        "validation_passed": true,
        "errors": []
      }
    },
    {
      "step_name": "tool_execution",
      "status": "ok",
      "duration_ms": 0.13,
      "details": {
        "tool_success": true,
        "error": null,
        "data_summary": "dict"
      }
    }
  ]
}
```

---

## 5. Defensive Execution and Error Handling

1. **Missing Required Arguments:** Returns `validation_error` detailing the missing parameter name and description.
2. **Type Mismatch:** Rejects invalid argument types with clear diagnostic messages (e.g. `Parameter 'a' must be a number, got str`).
3. **Graceful Refusal:** Out-of-domain requests return status `unsupported_request` with zero tool execution.
4. **Execution Fault Tolerance:** Unhandled exceptions inside tool bodies are captured by the registry and formatted as clean `execution_error` outcomes.
