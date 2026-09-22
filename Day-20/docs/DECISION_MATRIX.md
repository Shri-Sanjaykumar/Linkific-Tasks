# Function Calling Decision Matrix

This matrix documents the selection criteria, required inputs, expected outputs, selection rationales, and error notes for **10 realistic user requests** evaluated by the Function Calling Engine.

---

## Decision Matrix Table

| Request ID | User Request | Selected Tool / Function | Required Input | Expected Output | Reason for Selection | Tool Chaining Required | Error / Limitation Notes |
| :---: | :--- | :---: | :--- | :--- | :--- | :---: | :--- |
| **REQ-01** | "Calculate 450 divided by 15" | `calculator` | `a: 450.0, b: 15.0, operation: "divide"` | `{"operation": "divide", "a": 450.0, "b": 15.0, "result": 30}` | Explicit arithmetic calculation request with division operator and two numeric operands. | No | Division-by-zero check enforced if divisor is 0; non-numeric inputs rejected. |
| **REQ-02** | "Search for latest documentation on LangGraph multi-actor workflows" | `web_search` | `query: "latest documentation on LangGraph multi-actor workflows"` | Structured search results containing titles, URLs, snippets, and relevance scores. | Informational query requiring technical reference lookup across documentation. | No | Operates over demonstration local index; labeled as mock; network timeout simulated via flag. |
| **REQ-03** | "Query employees with salary greater than 100000 from the company database" | `database_tool` | `operation: "query", query: "SELECT * FROM employees WHERE salary > ?", params: [100000]` | JSON list of matching employee records with names, departments, roles, and salaries. | Structured relational data query filtering table rows based on numeric criteria. | No | Parameterized queries prevent SQL injection; destructive SQL (DROP/DELETE) prohibited. |
| **REQ-04** | "Read and inspect the contents of sample_sales.csv" | `file_reader` | `file_path: "Day-20/data/sample_sales.csv"` | Structured file metadata (char count, line count, extension) and parsed CSV rows. | Direct file inspection request targeting an allowed local CSV data asset. | No | Path traversal blocked outside workspace; extension whitelisting enforced (.csv/.json/.txt/.md). |
| **REQ-05** | "What is the current weather and temperature in Bengaluru?" | `weather_tool` | `location: "Bengaluru", units: "celsius"` | Temperature (24.5°C), weather condition, humidity (68%), and wind metrics. | Real-time meteorological inquiry for a specific global metropolitan city. | No | Demonstration database; numeric or empty city strings rejected; service outage simulated via flag. |
| **REQ-06** | "Draft an email to mentor@linkific.internal with subject Status Report" | `email_tool` | `recipient: "mentor@linkific.internal", subject: "Status Report", body: "...", action: "draft"` | Draft object with unique `draft_id`, timestamp, and status `draft_saved`. | Email composition and recipient address validation request. | No | Recipient syntax validated via RFC regex; mock simulation only (no live SMTP transmission). |
| **REQ-07** | "How many days are between 2026-09-01 and 2026-09-22?" | `date_tool` | `operation: "date_diff", start_date: "2026-09-01", end_date: "2026-09-22"` | `{"days_difference": 21, "hours_difference": 504, "is_positive": true}` | Calendar interval calculation between two ISO 8601 dates. | No | Strict ISO 8601 format checking; invalid leap days (e.g. 2026-02-29) rejected defensively. |
| **REQ-08** | "Compute the average revenue from sample_sales.csv dataset" | `data_analyzer` | `operation: "average", file_path: "Day-20/data/sample_sales.csv", target_column: "revenue"` | `{"operation": "average", "target_column": "revenue", "average": 4950.0, "sample_size": 10}` | Statistical aggregation request over a numeric column in tabular data. | No | Non-numeric entries ignored with warning; missing column names trigger structured error. |
| **REQ-09** | "Look up Linkific company policy guidelines on leave entitlement and core collaboration hours" | `company_search` | `query: "leave entitlement and core collaboration hours", top_k: 3` | Top relevant policy excerpts, document ID (`DOC-POL-001`), section headers, and overlap scores. | Organizational governance and corporate policy lookup in company knowledge base. | No | Indexes local synthetic project policies; empty queries rejected; category filter supported. |
| **REQ-10** | "Tell me a fairy tale about a magic unicorn dancing on the rainbow clouds" | `None` *(Refused)* | `N/A` | Controlled refusal: `"I cannot fulfill this request because no registered tool matches the requested capability."` | Creative fiction request falling outside the operational boundaries of registered tools. | No | Refused gracefully with status `unsupported_request` to prevent hallucination or unrelated tool calling. |

---

## Key Observations

1. **Deterministic Dispatching:** 9 out of 10 requests were routed to specialized capability tools with 100% precision.
2. **Defensive Isolation:** In REQ-07, the Date Tool was prioritized ahead of the Calculator to prevent ISO date strings with hyphens (`2026-09-01`) from being misinterpreted as mathematical subtractions (`2026 - 9`).
3. **Graceful Refusal:** In REQ-10, the system avoided hallucinating or forcing an unrelated tool, returning a structured refusal and recording an auditable operational trace.
