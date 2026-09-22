# Day 20 Workflow Notes: Function Calling & Tool Chaining Architecture

## 1. System Architecture Overview

The Day 20 architecture provides a complete, deterministic, and enterprise-grade **Tool Creation and Function Calling Engine**. It bridges the gap between unstructured user prompts and real execution environments without relying on mocked hallucinations or unsafe external code execution.

### Architectural Diagram

```
                 +----------------------------------+
                 |       User Natural Request       |
                 +-----------------+----------------+
                                   |
                                   v
                 +----------------------------------+
                 |     Function Calling Engine      |
                 |     (app/engine.py: process)     |
                 +-----------------+----------------+
                                   |
            +----------------------+----------------------+
            |                      |                      |
            v                      v                      v
  [Single Tool Request]   [Tool Chain Request]   [Unsupported Request]
            |                      |                      |
            |                      v                      v
            |             +------------------+    +---------------+
            |             | Execution Pipe   |    | Graceful      |
            |             | Step 1 -> Step 2 |    | Refusal       |
            |             +--------+---------+    +---------------+
            |                      |
            +----------+-----------+
                       |
                       v
       +-------------------------------+
       |   Argument Schema Validation  |
       |  (Type, Required, Enums)      |
       +---------------+---------------+
                       |
             +---------+---------+
             |                   |
        (Valid args)      (Invalid args)
             |                   |
             v                   v
+------------------------+  +--------------------+
|     Tool Registry      |  | Validation Error   |
|   (app/registry.py)    |  | Envelope           |
+-----------+------------+  +--------------------+
            |
            v
+-----------------------------------------------------------------------------------+
|                           10 Specialized Active Tools                             |
|                                                                                   |
|  - calculator      : AST arithmetic with zero-division guard                      |
|  - web_search      : Live Wikipedia/DuckDuckGo API with offline local index       |
|  - database_tool   : Read-only SQLite engine with parameterized SQL               |
|  - file_reader     : Safe disk reader with path-traversal & extension defense     |
|  - weather_tool    : Live Open-Meteo geocoded weather with cached fallback        |
|  - email_tool      : RFC 822 MIME draft generator, disk persistence & outbox log |
|  - date_tool       : Calendar interval & offset engine with ISO verification      |
|  - data_analyzer   : In-memory tabular metrics, column audits & averages          |
|  - company_search  : Knowledge-base policy index & relevance scoring              |
|  - pdf_reader      : Multi-page PDF text extraction, metadata & keyword search   |
+-----------------------------------+-----------------------------------------------+
                                    |
                                    v
                 +----------------------------------+
                 |     Execution Trace & Logger     |
                 |  (duration, steps, status, JSON) |
                 +----------------------------------+
```

---

## 2. Tool Registration & Schema Generation

All tools are encapsulated via `ToolDefinition` objects paired with callable Python functions in `ToolRegistry` (`app/registry.py`).

1. **Standardized Parameter Contracts:** Each tool parameter specifies `name`, `type` (`string`, `number`, `integer`, `boolean`, `array`, `object`), `description`, `required`, and optional `enum` constraints.
2. **Schema Introspection:** `registry.get_all_schemas()` outputs an OpenAI-compatible function definition array, allowing direct plug-and-play integration with frontier LLMs (GPT-4o, Claude 3.5, Gemini 1.5/2.0).
3. **Execution Boundary:** When calling `registry.execute(tool_name, arguments)`, the registry validates parameter presence and types *before* invoking the underlying callable. Any internal exceptions are trapped and returned as structured failure envelopes.

---

## 3. Function Calling & Selection Pipeline

The `FunctionCallingEngine` (`app/engine.py`) coordinates intent identification and argument binding:

1. **Semantic Isolation:**
   - Evaluates date patterns prior to arithmetic evaluation to prevent ISO date strings (e.g. `2026-09-01`) from triggering arithmetic subtraction (`2026 - 9`).
   - Dispatches database requests with parameterized values to prevent SQL injection vulnerabilities.
   - Extracts city names and units for dynamic weather telemetry.
2. **Dynamic Execution with Offline Resilience:**
   - **Weather:** Calls Open-Meteo's geocoding API to resolve latitude/longitude, then calls Open-Meteo's forecast API for live temperature and wind speed. If network is unavailable, seamlessly falls back to curated offline telemetry cache.
   - **Web Search:** Queries Wikipedia OpenSearch and DuckDuckGo Instant Answer APIs for real-time snippets, falling back to local documentation index when offline.
   - **Email:** Emits real RFC 822 `.eml` and structured `.json` files to `Day-20/data/drafts/` with disk inspection (`list_drafts`) and audit logging to `Day-20/data/outbox.log`.
   - **PDF Reader:** Ingests `data/company_handbook.pdf` via `pypdf`, providing page-by-page text, metadata inspection, and keyword searching across pages.
3. **Graceful Refusal:**
   - Out-of-domain requests (e.g. fantasy tales, poetry, general conversation) return `unsupported_request` envelopes without invoking any tool or hallucinating outputs.

---

## 4. Multi-Step Tool Chaining Workflows

Real-world AI systems routinely require chaining the output of one tool as the input of another. The engine implements three deterministic multi-step pipelines:

### Chain 1: File Reader -> Tabular Data Analyzer
- **Step 1 (`file_reader`):** Reads raw tabular content from `Day-20/data/sample_sales.csv`.
- **Step 2 (`data_analyzer`):** Feeds parsed CSV text into the data analyzer to compute column summaries, missing value profiles, and statistical metrics.
- **Auditing:** Both steps are recorded in the execution trace with intermediate durations and outputs.

### Chain 2: Database Query Tool -> Data Analyzer
- **Step 1 (`database_tool`):** Executes parameterized query `SELECT * FROM employees WHERE department = ?` (`Engineering`).
- **Step 2 (`data_analyzer`):** Pipes the resulting database rows into the data analyzer to compute the average salary for the engineering department (`115000.0`).

### Chain 3: Date Tool -> Calculator
- **Step 1 (`date_tool`):** Computes calendar day interval between project milestone dates (`2026-09-01` to `2026-09-22` -> `21` days).
- **Step 2 (`calculator`):** Passes the interval (`21`) to the calculator to multiply by the daily intern rate (`150.0`), producing total compensation (`3150.0`).

### Failure Propagation Guardrail
If any step in a multi-step chain returns `success=False` (e.g. missing file, invalid SQL syntax), the chain execution halts immediately. The failed step's error envelope is propagated upstream, and subsequent steps are skipped safely.

---

## 5. Defensive Error Handling & Guardrails

The implementation implements **Defense in Depth**:
1. **Pre-Execution:**
   - Parameter type enforcement.
   - Missing required argument detection.
   - Path traversal prevention (`../` escapes blocked).
   - Destructive SQL command blocking (`DROP`, `DELETE`, `TRUNCATE`).
2. **Runtime Protection:**
   - Division-by-zero protection in Calculator.
   - Corrupt or encrypted PDF file catching in PDF Reader.
   - Non-leap year calendar date validation (`2026-02-29` rejected).
   - Network failure simulation via explicit test flags (`simulate_service_failure=True`).
3. **Post-Execution:**
   - Unified `ToolResult` format across all 10 tools.
   - Full structured execution traces saved in `outputs/` and CLI logs.

---

## 6. Execution Trace & Auditing

Every invocation generates a uniquely identified `ExecutionTrace` (`TRC-XXXXXX`):
- Measures total wall-clock duration in milliseconds.
- Captures per-step statuses, tool names, durations, and diagnostic summaries.
- Provides complete operational visibility for debugging and enterprise compliance.
