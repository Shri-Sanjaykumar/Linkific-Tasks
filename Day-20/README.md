# Day 20 — Tool Creation, Function Calling, Tool Chaining, and Error Handling

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.13-green.svg)](https://docs.pydantic.dev/)
[![PyTest](https://img.shields.io/badge/Tests-58%20Passed-brightgreen.svg)](tests/test_tools.py)
[![Status](https://img.shields.io/badge/Status-Completed%20%26%20Dynamic-success.svg)]()

Production-grade implementation of **Tool Creation**, **Function Calling**, **Multi-Tool Chaining**, and **Defensive Error Handling** built for the **Linkific AI/ML Internship**.

---

## 📋 Table of Contents
1. [Learning Objectives](#-learning-objectives)
2. [Project Architecture](#-project-architecture)
3. [Implemented Tools Suite (10 Tools)](#-implemented-tools-suite-10-tools)
4. [Function Calling Engine & Tool Selection Matrix](#-function-calling-engine--tool-selection-matrix)
5. [Tool Chaining Workflows](#-tool-chaining-workflows)
6. [Defensive Error Handling](#-defensive-error-handling)
7. [Company Project Practical Tools (All 4 Examples)](#-company-project-practical-tools-all-4-examples)
8. [Setup & Execution Instructions](#-setup--execution-instructions)
9. [Automated Verification Results (58 Tests)](#-automated-verification-results-58-tests)
10. [Documentation Index](#-documentation-index)

---

## 🎯 Learning Objectives

This project systematically implements and demonstrates:
1. **Tool Creation:** Modular implementations of 10 discrete tools (including 4 comprehensive project practical tools: Database Query Tool, CSV Analyzer, PDF Reader, and Company Search Tool) with explicit Pydantic schemas, strict type enforcement, division-by-zero defense, and path safety.
2. **Function Calling:** Centralized `ToolRegistry` with OpenAI-compatible JSON Schema generation, pre-execution argument validation, natural language intent mapping, and auditable execution tracing without private CoT leakage.
3. **Tool Chaining:** Three end-to-end multi-tool pipelines with intermediate payload routing, state transformations, and fail-fast abort mechanics.
4. **Error Handling:** 18+ defensive failure scenarios handled with standardized `ToolResult` envelopes, preventing unhandled crashes.
5. **Dynamic Real Execution:** Upgraded beyond static mocks to live weather telemetry (Open-Meteo geocoding), live web search (Wikipedia/DuckDuckGo API), RFC 822 email MIME drafting with disk persistence, and native PDF document parsing with `pypdf`.

---

## 🏗 Project Architecture

```text
Day-20/
├── README.md                      # Primary project overview and execution guide
├── requirements.txt               # Pinned dependencies (pydantic, pypdf, reportlab, pytest)
├── run_tools.py                   # Master CLI runner (tools, chains, matrix, interactive)
├── app/
│   ├── __init__.py                # Package exports
│   ├── schemas.py                 # Pydantic schemas (ToolResult, Trace, Chain)
│   ├── registry.py                # Central ToolRegistry & schema generator
│   ├── engine.py                  # Function Calling Engine & intent router
│   ├── chains.py                  # Multi-tool chaining pipelines
│   ├── tools/
│   │   ├── __init__.py            # Tool registration helper (10 tools active)
│   │   ├── calculator.py          # Math tool (+, -, *, /) with zero-division guard
│   │   ├── web_search.py          # Dynamic search (Wikipedia/DuckDuckGo API + offline fallback)
│   │   ├── database_tool.py       # SQLite parameterized query & schema inspector
│   │   ├── file_reader.py         # Safe file reader (.csv, .json, .txt, .md, .py, .sql)
│   │   ├── weather_tool.py        # Dynamic weather telemetry (Open-Meteo geocoding + cached fallback)
│   │   ├── email_tool.py          # RFC 822 MIME draft generator, disk persistence & outbox log
│   │   ├── date_tool.py           # ISO 8601 calendar arithmetic & difference
│   │   ├── data_analyzer.py       # Tabular summary statistics & column audits
│   │   ├── company_search.py      # Company practical tool (Linkific policies)
│   │   └── pdf_reader.py          # Practical tool: Native PDF parser (text, metadata, keyword search)
│   └── utils.py                   # Trace and markdown report formatters
├── data/
│   ├── company_records.db         # SQLite database with employees and projects
│   ├── sample_sales.csv           # Financial tabular dataset
│   ├── sample_employees.json      # Structured personnel records
│   ├── sample_policy.txt          # Linkific corporate governance document
│   ├── company_handbook.pdf       # Multi-page corporate handbook PDF for pdf_reader
│   ├── malformed.csv              # Corrupted file for negative testing
│   ├── drafts/                    # Dynamic RFC 822 .eml and .json email drafts
│   └── outbox.log                 # Simulated outbound email audit log
├── diagrams/
│   ├── function_calling_workflow.mmd  # Function calling architecture diagram
│   ├── tool_chaining_flow.mmd         # 3-pipeline chaining diagram
│   └── error_handling_flow.mmd        # Multi-tiered error defense diagram
├── docs/
│   ├── TOOL_CREATION.md               # Detailed 10-tool specifications & schemas
│   ├── FUNCTION_CALLING.md            # Registry, selection & tracing specs
│   ├── TOOL_SELECTION_MATRIX.md       # Tool selection matrix table with candidate evaluations
│   ├── DECISION_MATRIX.md             # Function calling decision matrix table
│   ├── WORKFLOW_NOTES.md              # Architecture, pipelines & production recommendations
│   ├── TOOL_CHAINING.md               # Multi-tool pipeline analysis
│   ├── ERROR_HANDLING.md              # 18-scenario error handling taxonomy
│   ├── COMPANY_PROJECT_TOOL.md        # All 4 project practical tools documented
│   └── TESTING_AND_EXECUTION_REPORT.md# 58/58 automated pytest audit report
├── examples/
│   ├── single_tool_calls.json         # Real snapshot of tool outputs
│   ├── tool_chain_execution.json      # Real snapshot of 3 chain executions
│   ├── error_scenarios.json           # Real snapshot of error handling outputs
│   └── decision_matrix_results.json   # Real snapshot of decision matrix requests
├── outputs/
│   ├── execution_trace.md             # Rendered operational execution traces
│   ├── pytest_results.txt             # Raw pytest output (58/58 passed)
│   └── verification_summary.md        # Comprehensive deliverables checklist
└── tests/
    ├── __init__.py
    └── test_tools.py                  # 58 automated unit and integration tests
```

---

## 🛠 Implemented Tools Suite (10 Tools)

| # | Tool Identifier | Module | Description & Primary Capabilities | Operational Mode |
| :---: | :--- | :--- | :--- | :---: |
| 1 | `calculator` | `app.tools.calculator` | Arithmetic calculations (`add`, `subtract`, `multiply`, `divide`) with division-by-zero defense. | **Real AST Math** |
| 2 | `web_search` | `app.tools.web_search` | Dynamic technical documentation & article search via Wikipedia & DuckDuckGo APIs with offline cache. | **Live API + Fallback** |
| 3 | `database_tool` | `app.tools.database_tool` | Parameterized SQLite queries (`company_records.db`), schema introspection, and read-only protection. | **Real SQLite DB** |
| 4 | `file_reader` | `app.tools.file_reader` | Path-safe reader supporting `.csv`, `.json`, `.txt`, `.md`, `.py`, `.sql` with encoding and traversal checks. | **Real File System** |
| 5 | `weather_tool` | `app.tools.weather_tool` | Real-time meteorological telemetry for global cities (Chennai, Bengaluru, London, Tokyo) via Open-Meteo. | **Live API + Fallback** |
| 6 | `email_tool` | `app.tools.email_tool` | RFC 822 MIME message generator, `.eml` & `.json` disk persistence (`data/drafts/`), and outbox logging. | **Real MIME & Disk** |
| 7 | `date_tool` | `app.tools.date_tool` | Calendar math, ISO 8601 validation, interval calculation (`days_between`), and date offsets. | **Real Datetime Math** |
| 8 | `data_analyzer` | `app.tools.data_analyzer` | Tabular/JSON statistical profiling (means, extrema, row counts, null audits, summaries). | **Real Statistics** |
| 9 | `company_search` | `app.tools.company_search` | **Practical Tool:** Lexical section retrieval across Linkific policy guidelines (`sample_policy.txt`). | **Real Knowledge Base** |
| 10 | `pdf_reader` | `app.tools.pdf_reader` | **Practical Tool:** Native PDF reader (`pypdf`) with page text extraction, metadata, and keyword search. | **Real PDF Engine** |

---

## 🤖 Function Calling Engine & Tool Selection Matrix

The `FunctionCallingEngine` (`app.engine`) handles tool selection, argument extraction, argument validation against schemas, and operational execution tracing.

### Tool Selection Matrix Summary

| Request ID | User Request | Selected Tool | Output Summary | Status |
| :---: | :--- | :---: | :--- | :---: |
| **REQ-01** | "Calculate 450 divided by 15" | `calculator` | Result: `30` | `success` |
| **REQ-02** | "Search for latest documentation on LangGraph..." | `web_search` | 5 relevant documentation results | `success` |
| **REQ-03** | "Query employees with salary greater than 100000..." | `database_tool` | 3 employee records | `success` |
| **REQ-04** | "Read and inspect the contents of sample_sales.csv" | `file_reader` | 10 CSV rows parsed, 11 lines | `success` |
| **REQ-05** | "What is the current weather in Chennai?" | `weather_tool` | Live geocoded telemetry: temp, humidity, condition | `success` |
| **REQ-06** | "Draft an email to mentor@linkific.internal..." | `email_tool` | RFC 822 draft saved to `data/drafts/` | `success` |
| **REQ-07** | "How many days are between 2026-09-01 and 2026-09-22?" | `date_tool` | 21 days difference | `success` |
| **REQ-08** | "Compute the average revenue from sample_sales.csv" | `data_analyzer` | Mean revenue: `$4,950.00` | `success` |
| **REQ-09** | "Look up Linkific company policy on leave entitlement..." | `company_search` | `DOC-POL-001` Section 3 (Leave Rules) | `success` |
| **REQ-10** | "Extract text and search for compliance in company_handbook.pdf" | `pdf_reader` | Extracted matching snippets from pages 1 & 2 | `success` |
| **REQ-11** | "Tell me a fairy tale about a magic unicorn..." | `None` *(Refused)* | Controlled refusal (out-of-domain) | `unsupported` |

*Detailed decision matrix documentation available in [`docs/TOOL_SELECTION_MATRIX.md`](docs/TOOL_SELECTION_MATRIX.md) and [`docs/DECISION_MATRIX.md`](docs/DECISION_MATRIX.md).*

---

## 🔗 Tool Chaining Workflows

The `ToolChainPipeline` (`app.chains`) provides 3 concrete multi-tool pipelines:

1. **Pipeline 1 (File Reader ➔ Data Analyzer):**
   Reads `sample_sales.csv` on disk, extracts the parsed record structure, and routes it to `data_analyzer` to generate full summary statistics.
2. **Pipeline 2 (Database Tool ➔ Data Analyzer):**
   Executes `SELECT salary, tenure_years FROM employees;` on SQLite, feeds the returned records to `data_analyzer`, and calculates the mean salary (`$105,166.67`).
3. **Pipeline 3 (Date Tool ➔ Calculator):**
   Calculates the interval in days between milestones (`2026-09-01` to `2026-09-22` -> 21 days) and feeds the value to `calculator` to multiply by `150.0` daily rate, producing `3150.0`.

*Detailed chaining documentation available in [`docs/TOOL_CHAINING.md`](docs/TOOL_CHAINING.md) and [`docs/WORKFLOW_NOTES.md`](docs/WORKFLOW_NOTES.md).*

---

## 🛡 Defensive Error Handling

All tools wrap outputs in the `ToolResult` envelope, trapping:
- Type errors and non-numeric operands.
- Zero-division in arithmetic.
- Missing files and unsupported extensions (`.db`, `.exe`).
- Directory traversal outside the project sandbox.
- SQL syntax errors, missing tables, and destructive queries (`DROP TABLE`).
- Simulated network timeouts (HTTP 503/504).
- Malformed email syntax.
- Non-existent leap year dates (e.g., `2026-02-29`).
- Empty datasets or missing columns.
- Corrupted or encrypted PDF files.

*Detailed taxonomy available in [`docs/ERROR_HANDLING.md`](docs/ERROR_HANDLING.md).*

---

## 🏢 Company Project Practical Tools (All 4 Examples)

The assignment asked for at least one practical tool relevant to the company domain. The project implements **all four**:
1. **Database Query Tool (`database_tool`):** Real parameterized SQLite queries and schema inspection.
2. **CSV Data Analyzer (`data_analyzer`):** Statistical analysis and data quality auditing.
3. **PDF Reader (`pdf_reader`):** Real PDF document extraction and keyword search with `pypdf`.
4. **Company Search Tool (`company_search`):** Lexical and section retrieval across Linkific policy guidelines.

*Full details in [`docs/COMPANY_PROJECT_TOOL.md`](docs/COMPANY_PROJECT_TOOL.md).*

---

## 🚀 Setup & Execution Instructions

### 1. Prerequisites
- Python 3.10+
- Dependencies installed via:
  ```bash
  pip install -r Day-20/requirements.txt
  ```

### 2. Run All Demonstrations
```bash
python Day-20/run_tools.py --all
```

### 3. Run Specific Sections
```bash
python Day-20/run_tools.py --tools     # Run 10 individual tool demos
python Day-20/run_tools.py --chains    # Run 3 multi-tool chains
python Day-20/run_tools.py --errors    # Run defensive error handling tests
python Day-20/run_tools.py --matrix    # Run decision matrix requests
```

### 4. Run Interactive CLI
```bash
python Day-20/run_tools.py --interactive
```
*To terminate the interactive loop cleanly, enter `exit`, `quit`, or `q`.*

### 5. Run Automated Tests
```bash
pytest Day-20/tests/test_tools.py -v
```

---

## 📊 Automated Verification Results (58 Tests)

```text
============================= test session starts =============================
platform win32 -- Python 3.13.12, pytest-9.1.1, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: C:\projects\linkific\internship\Day-20\tests
plugins: anyio-4.15.1
collecting ... collected 58 items

..\Day-20\tests\test_tools.py::test_tool_registration_all_tools PASSED [  1%]
..\Day-20\tests\test_tools.py::test_tool_schema_export_json PASSED     [  3%]
...
..\Day-20\tests\test_tools.py::test_weather_chennai_query PASSED       [ 77%]
..\Day-20\tests\test_tools.py::test_email_tool_draft_persistence PASSED [ 93%]
..\Day-20\tests\test_tools.py::test_pdf_reader_handbook PASSED         [ 94%]
..\Day-20\tests\test_tools.py::test_pdf_reader_keyword_search PASSED   [ 96%]
..\Day-20\tests\test_tools.py::test_pdf_reader_missing_file PASSED     [ 98%]
..\Day-20\tests\test_tools.py::test_pdf_reader_unsupported_format PASSED [100%]

============================= 58 passed in 9.77s ==============================
```

---

## 📚 Documentation Index
- [Tool Selection Matrix](docs/TOOL_SELECTION_MATRIX.md)
- [Function Calling Documentation](docs/FUNCTION_CALLING.md)
- [Workflow Notes](docs/WORKFLOW_NOTES.md)
- [Company Project Practical Tools (All 4 Examples)](docs/COMPANY_PROJECT_TOOL.md)
- [Tool Creation Documentation](docs/TOOL_CREATION.md)
- [Function Calling Decision Matrix](docs/DECISION_MATRIX.md)
- [Tool Chaining Documentation](docs/TOOL_CHAINING.md)
- [Error Handling Notes](docs/ERROR_HANDLING.md)
- [Testing & Execution Report](docs/TESTING_AND_EXECUTION_REPORT.md)
- [Verification Summary](outputs/verification_summary.md)
