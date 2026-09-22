# Tool Creation Documentation

## 1. Architectural Overview

In production AI and autonomous agent systems, tools bridge the gap between static language generation and deterministic execution. Rather than relying on speculative reasoning or hallucinated outputs, an agent leverages specialized tools with strictly defined contracts, deterministic validation, and auditable error boundaries.

The Day 20 implementation provides a modular suite of **10 discrete tools** (including 4 comprehensive project practical tools: Database Query Tool, CSV Data Analyzer, PDF Reader, and Company Search Tool). Each tool adheres to the `ToolResult` unified envelope design pattern:

```python
class ToolResult(BaseModel):
    tool_name: str
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)
```

---

## 2. Core Tool Specifications

### 2.1 Calculator Tool (`calculator`)
- **Module:** `app.tools.calculator`
- **Purpose:** Executes validated arithmetic calculations with division-by-zero protection using safe AST arithmetic evaluation.
- **Supported Operations:** `add` (`+`), `subtract` (`-`), `multiply` (`*`), `divide` (`/`).
- **Input Parameters:**
  - `a` (`number`, required): First numeric operand.
  - `b` (`number`, required): Second numeric operand.
  - `operation` (`string`, required): Operation enum (`add`, `subtract`, `multiply`, `divide`).
- **Defensive Guardrails:**
  - Strict type verification (rejects non-numeric inputs and booleans).
  - Explicit check for `b == 0` when `operation == "divide"`, returning controlled failure without throwing unhandled exceptions.
- **Output Schema:**
  - `{"operation": str, "a": float, "b": float, "result": float | int}`

### 2.2 Web Search Tool (`web_search`)
- **Module:** `app.tools.web_search`
- **Purpose:** Dynamic search engine integration querying Wikipedia OpenSearch API and DuckDuckGo Instant Answer API in real-time, with automatic defensive fallback to a local technical documentation index.
- **Operational Mode:** Live network calls with automatic fallback. Uses standard HTTP User-Agent headers, strips HTML markup from snippets, and provides structured title/URL/snippet tuples.
- **Input Parameters:**
  - `query` (`string`, required): Search string or keywords.
  - `max_results` (`integer`, optional, default=5): Result limit.
  - `simulate_service_failure` (`boolean`, optional, default=False): Simulates upstream HTTP 503 gateway timeouts for resilience testing.
- **Defensive Guardrails:**
  - Empty or whitespace-only query rejection.
  - Automatic fallback to local technical index if network is unreachable or offline.
  - Upstream network failure simulation and recovery handling.
- **Output Schema:**
  - `{"query": str, "total_results": int, "results": List[Dict[str, Any]], "source": "live_api" | "local_technical_index"}`

### 2.3 Database Tool (`database_tool`)
- **Module:** `app.tools.database_tool`
- **Purpose:** Executes parameterized SQLite queries and schema introspection over relational database `data/company_records.db`.
- **Supported Operations:**
  - `query`: Executes parameterized read-only SELECT statements.
  - `read_table`: Reads all records from a specified table.
  - `get_schema`: Inspects database tables, column names, nullability, and primary keys.
- **Input Parameters:**
  - `operation` (`string`, required): `query`, `read_table`, or `get_schema`.
  - `query` (`string`, optional): SQL statement for `query` operation.
  - `table_name` (`string`, optional): Target table for `read_table` or `get_schema`.
  - `params` (`array`, optional): Positional parameters for SQL binding.
  - `db_path` (`string`, optional): Custom database path.
  - `simulate_connection_failure` (`boolean`, optional, default=False): Tests connection dropouts.
- **Defensive Guardrails:**
  - SQLite URI read-only connection mode (`file:...?mode=ro`).
  - Strict keyword filtering blocking destructive statements (`DROP`, `TRUNCATE`, `DELETE`, `ALTER`).
  - Table existence checks against `sqlite_master` prior to execution.
  - Parameterized binding preventing SQL injection vulnerabilities.

### 2.4 File Reader Tool (`file_reader`)
- **Module:** `app.tools.file_reader`
- **Purpose:** Reads and parses supported local files with encoding protection and directory traversal blocking.
- **Supported Extensions:** `.txt`, `.csv`, `.json`, `.md`, `.py`, `.sql`.
- **Input Parameters:**
  - `file_path` (`string`, required): Relative or absolute path to the file.
  - `max_chars` (`integer`, optional): Character truncation ceiling.
  - `encoding` (`string`, optional, default="utf-8"): Text encoding.
- **Defensive Guardrails:**
  - Path traversal checks preventing directory escapes beyond project workspace boundaries.
  - Extension whitelisting rejecting binary, executable, or compiled artifacts (`.db`, `.exe`, `.pyc`).
  - `UnicodeDecodeError` handling returning structured error rather than unhandled exception.
  - Local `data/` directory fallback resolving simple filenames to canonical repository data assets.

### 2.5 Weather Tool (`weather_tool`)
- **Module:** `app.tools.weather_tool`
- **Purpose:** Dynamic meteorological telemetry tool querying Open-Meteo's live geocoding and weather API in real-time, fetching live temperature (°C/°F), humidity, WMO weather condition code interpretation, and wind speed for any global city (e.g. Chennai, Bengaluru, New York, London, Tokyo).
- **Operational Mode:** Live API calls with automatic fallback to curated telemetry cache if offline or network unreachable.
- **Input Parameters:**
  - `location` (`string`, required): Name of city (e.g., Chennai, Bengaluru, New York, London, Tokyo).
  - `units` (`string`, optional, default="celsius"): `celsius` or `fahrenheit`.
  - `simulate_service_failure` (`boolean`, optional, default=False): Tests HTTP 504 gateway timeout resilience.
- **Defensive Guardrails:**
  - Purely numeric string rejection (e.g. rejecting "123456" as a location).
  - Empty location rejection.
  - WMO weather code to English descriptor mapping (Clear, Overcast, Rain, Snow, Thunderstorm).
  - Clean error formatting when city cannot be geocoded.

### 2.6 Email Tool (`email_tool`)
- **Module:** `app.tools.email_tool`
- **Purpose:** Dynamic email workflow tool generating RFC 822 MIME-compliant messages, validating recipient addresses, persisting `.eml` and `.json` draft files to disk (`data/drafts/`), listing existing drafts, and logging simulated outbound dispatches (`data/outbox.log`).
- **Supported Actions:** `validate`, `draft`, `simulate_send`, `list_drafts`.
- **Input Parameters:**
  - `recipient` (`string`, required for validate/draft/simulate_send): Recipient email address.
  - `subject` (`string`, required for draft/simulate_send): Message heading.
  - `body` (`string`, required for draft/simulate_send): Message body text.
  - `action` (`string`, optional, default="validate"): Action enum.
- **Defensive Guardrails:**
  - Strict regex pattern validation for email syntax (`^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$`).
  - Empty subject and empty body rejection for drafting and sending.
  - Safe directory creation for draft persistence without colliding filenames.

### 2.7 Date Tool (`date_tool`)
- **Module:** `app.tools.date_tool`
- **Purpose:** Deterministic calendar mathematics, interval calculation, ISO 8601 formatting, and timezone handling.
- **Supported Operations:**
  - `current_date`: Returns YYYY-MM-DD timestamp.
  - `current_datetime`: Returns full ISO timestamp.
  - `date_diff`: Computes days and hours elapsed between `start_date` and `end_date`.
  - `add_days`: Adds integer days to `start_date`.
  - `subtract_days`: Subtracts integer days from `start_date`.
- **Input Parameters:**
  - `operation` (`string`, required): Calendar operation enum.
  - `start_date` (`string`, optional): Base ISO date (YYYY-MM-DD).
  - `end_date` (`string`, optional): Target ISO date for comparison.
  - `days` (`integer`, optional): Days offset.
  - `tz_name` (`string`, optional, default="UTC"): Timezone label.
- **Defensive Guardrails:**
  - Strict ISO 8601 parsing (`%Y-%m-%d`, `%Y-%m-%dT%H:%M:%S`).
  - Rejection of invalid calendar dates (e.g. non-leap year `2026-02-29`).

### 2.8 Data Analyzer Tool (`data_analyzer`)
- **Module:** `app.tools.data_analyzer`
- **Purpose:** Computes comprehensive statistical profiles, column type audits, averages, extrema, and missing-value counts on CSV or JSON datasets.
- **Supported Operations:**
  - `summary`: Full distribution and column profile.
  - `row_count`: Total record count.
  - `column_info`: Inferred data types and column catalog.
  - `average`: Column arithmetic mean.
  - `min_max`: Column minimum and maximum values.
  - `missing_values`: Null and empty field frequency count.
- **Input Parameters:**
  - `operation` (`string`, optional, default="summary"): Analysis operation enum.
  - `data` (`object`, optional): Inline CSV text, JSON list of dicts, or table records.
  - `file_path` (`string`, optional): Path to disk dataset.
  - `target_column` (`string`, optional): Target column required for `average` or `min_max`.
- **Defensive Guardrails:**
  - Empty file and empty dataset rejection.
  - Non-numeric column detection when computing arithmetic averages.
  - Missing column error reporting.

### 2.9 Company Search Tool (`company_search`)
- **Module:** `app.tools.company_search`
- **Purpose:** Specialized domain tool indexing Linkific corporate governance policies, leave rules, and remote work guidelines directly with the function calling system.
- **Features:** Document section extraction, category filtering, term-overlap relevance scoring.

### 2.10 PDF Reader Tool (`pdf_reader`)
- **Module:** `app.tools.pdf_reader`
- **Purpose:** Real PDF document inspection tool powered by `pypdf`. Extracts structured text across pages, calculates document word counts, extracts metadata (Title, Author, Producer, Creation Date), and performs targeted keyword search across pages.
- **Supported Operations:**
  - `read_all`: Extracts full text from all pages with page markers.
  - `read_page`: Extracts text from a specified 1-indexed page.
  - `get_metadata`: Returns total page count, document info dictionary, and file size.
  - `search`: Scans all pages for a keyword or phrase, returning match count and page-specific snippets.
- **Input Parameters:**
  - `file_path` (`string`, required): Path to the PDF file.
  - `operation` (`string`, optional, default="read_all"): Operation enum.
  - `page_number` (`integer`, optional): Target 1-based page number for `read_page`.
  - `keyword` (`string`, optional): Target term for `search` operation.
  - `max_pages` (`integer`, optional): Maximum number of pages to process.
- **Defensive Guardrails:**
  - Validates `.pdf` file extension.
  - Verifies file existence on disk with fallback to `data/` folder.
  - Traps encrypted or password-protected PDFs gracefully.
  - Out-of-bounds page number validation.

---

## 3. Tool Registration & Introspection Mechanism

Tools are registered within a centralized `ToolRegistry` instance. Registration pairs a `ToolDefinition` metadata schema with its callable Python function.

```python
registry = ToolRegistry()
register_all_tools(registry)

# Inspect registered tools (10 tools active)
registered_tool_names = registry.list_tools()

# Export JSON schemas
openai_compatible_schemas = registry.get_all_schemas()

# Execute tool safely
result = registry.execute("calculator", {"a": 450, "b": 15, "operation": "divide"})
```
