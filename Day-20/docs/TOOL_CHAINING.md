# Tool Chaining Documentation

## 1. Overview of Tool Chaining

Tool chaining is the deterministic process of executing a sequence of specialized tools where the structured output of one tool serves as the input payload for the next tool in the pipeline.

Unlike isolated tool calls, tool chains require:
1. **Payload Translation:** Adapting and mapping intermediate keys from upstream tools to match the parameter schema of downstream tools.
2. **Intermediate Error Propagation:** Halting the chain immediately if any prerequisite step fails, preventing cascading invalid executions.
3. **End-to-End Tracing:** Logging timing, status, input mappings, and payloads for every link in the chain.

---

## 2. Concrete Implemented Pipelines

### Pipeline 1: File Reader ➔ Data Analyzer
- **Purpose:** Ingests local tabular files and generates statistical profiles and distribution metrics.
- **Step 1:** `file_reader`
  - **Input:** `file_path = "Day-20/data/sample_sales.csv"`
  - **Output:** `ToolResult` containing `parsed_structure` (list of row dicts) and `line_count`.
- **Payload Transition:** The pipeline extracts `parsed_structure` from Step 1 and binds it to `data` in Step 2.
- **Step 2:** `data_analyzer`
  - **Input:** `operation = "summary"`, `data = step1.data["parsed_structure"]`
  - **Output:** Full summary statistics (row count, numeric means, extrema, column classifications).
- **Execution Verification:**
  - Status: `PASSED`
  - Duration: `0.58 ms`
  - Final Outcome: Successfully analyzed 10 rows across columns `['product', 'units_sold', 'region', 'unit_price', 'revenue']`.

---

### Pipeline 2: Database Tool ➔ Data Analyzer
- **Purpose:** Extracts live relational records from SQLite and performs quantitative aggregations.
- **Step 1:** `database_tool`
  - **Input:** `operation = "query"`, `query = "SELECT salary, tenure_years FROM employees;"`
  - **Output:** `ToolResult` containing `records = [{"salary": 125000, "tenure_years": 4.5}, ...]` and `record_count = 6`.
- **Payload Transition:** The pipeline extracts `records` from Step 1, checks that the record count is greater than zero, and binds it to `data` with `target_column = "salary"`.
- **Step 2:** `data_analyzer`
  - **Input:** `operation = "average"`, `target_column = "salary"`, `data = step1.data["records"]`
  - **Output:** Mean salary, sample size, and non-numeric audit count.
- **Execution Verification:**
  - Status: `PASSED`
  - Duration: `0.59 ms`
  - Final Outcome: Average salary of `$105,166.67` across 6 employees.

---

### Pipeline 3: Date Tool ➔ Calculator
- **Purpose:** Calculates the calendar interval between milestone dates and computes total working hours or financial burn rate.
- **Step 1:** `date_tool`
  - **Input:** `operation = "date_diff"`, `start_date = "2026-09-01"`, `end_date = "2026-09-22"`
  - **Output:** `ToolResult` containing `days_difference = 21` and `hours_difference = 504`.
- **Payload Transition:** The pipeline extracts `days_difference = 21`, binds it to `a = 21.0`, binds `multiplier = 8.0` to `b = 8.0`, and sets `operation = "multiply"`.
- **Step 2:** `calculator`
  - **Input:** `a = 21.0`, `b = 8.0`, `operation = "multiply"`
  - **Output:** `{"operation": "multiply", "a": 21.0, "b": 8.0, "result": 168.0}`
- **Execution Verification:**
  - Status: `PASSED`
  - Duration: `0.13 ms`
  - Final Outcome: 21 milestone days * 8.0 hours/day = 168.0 total scheduled development hours.

---

## 3. Failure Propagation & Resilience

When an intermediate tool encounters an error, the `ToolChainPipeline` halts immediately:
- If Step 1 of Pipeline 1 attempts to read a non-existent file (`Day-20/data/non_existent.csv`), `file_reader` returns `FILE_NOT_FOUND`.
- The pipeline intercepts the failure, does not attempt Step 2, and returns a structured `ToolChainResult` with `success=False` and `error="Step 1 (file_reader) failed: File not found..."`.
- This behavior is verified in automated unit test `test_chain_failure_propagation()`.
