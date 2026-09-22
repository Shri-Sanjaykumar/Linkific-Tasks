# Tool Selection Matrix

This matrix documents the selection criteria, candidate tool evaluation, selected tool, reason for selection, parameters passed, expected output format, and operational notes for realistic user requests evaluated by the Function Calling Engine.

---

## Tool Selection Matrix Table

| Request ID | User Request | Candidate Tools | Selected Tool | Reason for Selection | Parameters Passed | Expected Output Format | Error / Limitation Notes |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- | :--- |
| **REQ-01** | "Calculate 450 divided by 15" | `calculator`, `date_tool` | `calculator` | Explicit arithmetic request with division operator and two numeric operands. | `{"a": 450.0, "b": 15.0, "operation": "divide"}` | JSON object with `result: 30.0` and operator metadata. | Division by zero checked; non-numeric inputs rejected. |
| **REQ-02** | "Search for latest documentation on LangGraph multi-actor workflows" | `web_search`, `company_search` | `web_search` | External technical inquiry requiring documentation lookup across web sources. | `{"query": "latest documentation on LangGraph multi-actor workflows", "max_results": 5}` | Array of search hits containing `title`, `url`, and `snippet`. | Live Wikipedia/DuckDuckGo lookup with offline fallback. |
| **REQ-03** | "Query employees with salary greater than 100000 from the company database" | `database_tool`, `file_reader` | `database_tool` | Structured relational query over SQLite database filtering table records. | `{"operation": "query", "query": "SELECT * FROM employees WHERE salary > ?", "params": [100000]}` | Array of row dictionaries with matching employee records. | Parameterized queries prevent SQL injection; destructive SQL blocked. |
| **REQ-04** | "Read and inspect the contents of sample_sales.csv" | `file_reader`, `data_analyzer` | `file_reader` | Direct file inspection request targeting a local CSV file on disk. | `{"file_path": "Day-20/data/sample_sales.csv"}` | File metadata (`total_lines`, `size_bytes`) and parsed CSV rows. | Path traversal blocked outside workspace; extension whitelisted. |
| **REQ-05** | "What is the current weather and temperature in Chennai?" | `weather_tool`, `web_search` | `weather_tool` | Real-time meteorological telemetry request for a specific metropolitan city. | `{"location": "Chennai", "units": "celsius"}` | Real temperature, humidity, WMO weather condition, and wind speed. | Live Open-Meteo geocoding & telemetry with cached fallback. |
| **REQ-06** | "Draft an email to mentor@linkific.internal with subject Status Report" | `email_tool`, `file_reader` | `email_tool` | Email composition and recipient validation request. | `{"recipient": "mentor@linkific.internal", "subject": "Status Report", "body": "...", "action": "draft"}` | RFC 822 draft ID, timestamp, and saved status. | RFC regex syntax validation; draft saved to disk as `.eml` and `.json`. |
| **REQ-07** | "How many days are between 2026-09-01 and 2026-09-22?" | `date_tool`, `calculator` | `date_tool` | Calendar interval calculation between two ISO 8601 dates. | `{"operation": "date_diff", "start_date": "2026-09-01", "end_date": "2026-09-22"}` | `{"days_difference": 21, "hours_difference": 504, "is_positive": true}` | Evaluated before calculator to prevent date hyphens parsed as minus. |
| **REQ-08** | "Compute the average revenue from sample_sales.csv dataset" | `data_analyzer`, `calculator` | `data_analyzer` | Statistical aggregation over a tabular dataset column. | `{"operation": "average", "file_path": "Day-20/data/sample_sales.csv", "target_column": "revenue"}` | `{"operation": "average", "target_column": "revenue", "average": 4950.0}` | Non-numeric entries handled; missing columns return error. |
| **REQ-09** | "Look up Linkific company policy guidelines on leave entitlement and core hours" | `company_search`, `web_search` | `company_search` | Internal company policy inquiry targeting corporate knowledge base. | `{"query": "leave entitlement and core hours", "top_k": 3}` | Matched policy excerpts, document ID (`DOC-POL-001`), and relevance. | Indexes local corporate policy files; category filtering supported. |
| **REQ-10** | "Extract text and search for compliance guidelines in company_handbook.pdf" | `pdf_reader`, `file_reader` | `pdf_reader` | Native PDF document text extraction and keyword search. | `{"file_path": "Day-20/data/company_handbook.pdf", "operation": "search", "keyword": "compliance"}` | Total page count, matching pages array, and extracted snippets. | Handled by `pypdf`; encrypted files caught; page bounds validated. |
| **REQ-11** | "Tell me a fairy tale about a magic unicorn dancing on the rainbow clouds" | All 10 Tools | `None` *(Refused)* | Creative writing request outside operational scope of registered tools. | `N/A` | Controlled refusal envelope with status `unsupported_request`. | Refused gracefully to prevent hallucination or unrelated tool calling. |

---

## Key Observations

1. **Deterministic Dispatching:** All domain requests are routed to specialized capability tools with 100% precision.
2. **Defensive Disambiguation:** In REQ-07, the Date Tool is evaluated ahead of the Calculator to ensure date hyphens (`2026-09-01`) are not misinterpreted as mathematical subtraction.
3. **Format-Specific Routing:** In REQ-10, PDF documents are routed to the specialized `pdf_reader` using `pypdf`, while text/CSV/JSON files are routed to `file_reader`.
4. **Graceful Refusal:** In REQ-11, out-of-domain requests are cleanly refused rather than invoking inappropriate tools.
