# Company Project Practical Tools

## 1. Context and Syllabus Requirements

The internship task objective specifies:
> "Design and implement at least one project practical tool relevant to the company or internship domain:
> Examples:
> - Database query tool
> - CSV analyzer
> - PDF reader
> - Company search tool"

Rather than implementing merely one example, the Day 20 architecture implements **all four** suggested project practical tools to provide an exhaustive, enterprise-grade practical demonstration:

1. **Database Query Tool (`database_tool`)**: Real relational SQLite engine with schema reflection, parameterized queries, and read-only safety guardrails.
2. **CSV Data Analyzer (`data_analyzer`)**: Comprehensive statistical profiling, column type deduction, numerical means, extrema, and missing-value diagnostics on tabular datasets.
3. **PDF Reader Tool (`pdf_reader`)**: Real multi-page PDF document parser extracting structured text, word counts, document metadata, and keyword searches using `pypdf`.
4. **Company Search Tool (`company_search`)**: Internal corporate knowledge base search tool indexing company policies, leave entitlements, remote work guidelines, and onboarding procedures.

---

## 2. Practical Tool 1: PDF Reader Tool (`pdf_reader`)

### 2.1 Purpose & Real-World Use Case
In an engineering or AI/ML workflow, reading real document formats like PDFs is essential for ingest pipelines, compliance verification, and multi-modal assistants. The `pdf_reader` tool parses native PDF files on disk using the high-performance `pypdf` engine.

### 2.2 Input Schema
- `file_path` (`string`, required): Path to the target PDF file (e.g., `Day-20/data/company_handbook.pdf`).
- `operation` (`string`, optional, default="read_all"): Operation enum (`read_all`, `read_page`, `get_metadata`, `search`).
- `page_number` (`integer`, optional): Specific 1-based page to extract when `operation="read_page"`.
- `keyword` (`string`, optional): Search term when `operation="search"`.
- `max_pages` (`integer`, optional): Safety limit on number of pages to inspect.

### 2.3 Output Schema & Example Execution
```json
{
  "operation": "search",
  "file_name": "company_handbook.pdf",
  "keyword": "compliance",
  "total_matches": 2,
  "pages_with_matches": [1, 2],
  "matches": [
    {
      "page_number": 1,
      "snippet": "...standards and corporate compliance. All interns and full-time engineers must uphold..."
    },
    {
      "page_number": 2,
      "snippet": "...security audits and data privacy compliance. For compliance inquiries, contact..."
    }
  ]
}
```

### 2.4 Defensive Guardrails
- Validates file extension is strictly `.pdf`.
- Checks for file existence with automatic fallback to project `data/` directory.
- Catches encrypted PDFs with clean error messaging.
- Verifies page boundaries preventing `IndexError`.

---

## 3. Practical Tool 2: Company Policy Search Tool (`company_search`)

### 3.1 Purpose & Synergy with Previous Days
Continues the organizational knowledge base established in Days 16–19 (RAG, FastAPI service, ReAct Agent, and LangGraph workflow). Allows querying Linkific corporate policies, leave rules, core hours, and onboarding standards.

### 3.2 Input Schema
- `query` (`string`, required): Search string (e.g. `"leave entitlement and core collaboration hours"`).
- `category` (`string`, optional): Optional category filter (`Corporate Policy`, `Onboarding`, `Leave`).
- `top_k` (`integer`, optional, default=3): Maximum top policy sections to return.

### 3.3 Output Schema
```json
{
  "query": "remote work and hardware allowance",
  "category_filter": null,
  "matches_count": 1,
  "matches": [
    {
      "document_id": "DOC-POL-001",
      "category": "Corporate Policy",
      "heading": "2. REMOTE WORK REIMBURSEMENT AND TOOL ACCESS",
      "excerpt": "Interns and engineers are provided standard cloud infrastructure credentials...",
      "relevance_score": 0.8,
      "source_file": "sample_policy.txt"
    }
  ]
}
```

---

## 4. Practical Tool 3: Database Query Tool (`database_tool`)

### 4.1 Purpose
Provides structured SQL access over `data/company_records.db`, allowing users and agents to query employee rosters, department metrics, and salaries without writing boilerplate Python code.

### 4.2 Security & Safety Guardrails
- **Read-Only Enforcement:** Uses SQLite URI `file:...?mode=ro` preventing accidental disk modification.
- **Destructive Query Blocking:** Rejects `DROP`, `DELETE`, `TRUNCATE`, `ALTER`, `INSERT`, `UPDATE` statements via pre-execution token scanning.
- **SQL Injection Defense:** All queries support parameterized execution (`?` placeholders with bound tuples).
- **Schema Reflection:** `get_schema` introspects table schemas, column types, nullability, and primary keys.

---

## 5. Practical Tool 4: Tabular Data Analyzer (`data_analyzer`)

### 5.1 Purpose
Performs dynamic in-memory statistical and data-quality analysis over tabular files (`sample_sales.csv`) or structured JSON payloads.

### 5.2 Supported Operations
- `summary`: Computes total rows, column catalog, numerical stats, and null counts.
- `row_count`: Returns total row count.
- `column_info`: Analyzes column types and sample entries.
- `average`: Computes arithmetic mean of a specified numerical column (e.g., `revenue`).
- `min_max`: Returns minimum and maximum values of a numerical column.
- `missing_values`: Profiles null/empty values per column.

---

## 6. Automated Verification Summary

All four project practical tools are validated in `Day-20/tests/test_tools.py` with 100% test pass rate:

| Practical Tool | Test Cases | Status |
| :--- | :--- | :---: |
| **PDF Reader Tool** | `test_pdf_reader_handbook`, `test_pdf_reader_keyword_search`, `test_pdf_reader_missing_file`, `test_pdf_reader_unsupported_format` | ✅ PASSED |
| **Company Search Tool** | `test_company_search_policy_query`, `test_company_search_empty_query`, `test_company_search_category_filter` | ✅ PASSED |
| **Database Query Tool** | `test_database_get_schema`, `test_database_read_table`, `test_database_parameterized_query`, `test_database_syntax_error`, `test_database_missing_table`, `test_database_destructive_query_blocked`, `test_database_connection_failure` | ✅ PASSED |
| **Data Analyzer Tool** | `test_data_analyzer_summary_csv`, `test_data_analyzer_row_count`, `test_data_analyzer_column_info`, `test_data_analyzer_average`, `test_data_analyzer_min_max`, `test_data_analyzer_missing_values`, `test_data_analyzer_missing_column`, `test_data_analyzer_empty_dataset` | ✅ PASSED |
