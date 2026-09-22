"""
Day 20 — Database Tool
Executes safe, parameterized SQLite operations over local synthetic database.
Handles connection errors, syntax errors, missing tables, and missing records gracefully.
"""

import os
import sqlite3
from typing import Optional, List, Dict, Any
from ..schemas import ToolResult, ToolDefinition, ToolParameter


def _get_default_db_path() -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_dir, "data", "company_records.db")


def database_tool(
    operation: str,
    query: Optional[str] = None,
    table_name: Optional[str] = None,
    params: Optional[List[Any]] = None,
    db_path: Optional[str] = None,
    simulate_connection_failure: bool = False
) -> ToolResult:
    """
    Executes database operations:
    - 'query': Executes a parameterized SELECT query.
    - 'read_table': Reads all records from specified table.
    - 'get_schema': Introspects table structure and columns.
    """
    target_db = db_path or _get_default_db_path()
    op = str(operation).strip().lower()
    parameters = params or []

    # 1. Connection failure handling
    if simulate_connection_failure:
        return ToolResult.fail(
            "database_tool",
            "Database connection failed: operational timeout or host unreachable.",
            metadata={"db_path": target_db, "error_code": "DB_CONNECTION_ERROR"}
        )

    if not os.path.exists(target_db):
        return ToolResult.fail(
            "database_tool",
            f"Database file not found at path: '{target_db}'.",
            metadata={"db_path": target_db, "error_code": "DB_FILE_NOT_FOUND"}
        )

    try:
        # Connect in read-only URI mode to prevent accidental mutation/dropping
        uri_path = f"file:{os.path.abspath(target_db)}?mode=ro"
        conn = sqlite3.connect(uri_path, uri=True, timeout=5.0)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
    except Exception as e:
        return ToolResult.fail(
            "database_tool",
            f"Failed to open database connection: {str(e)}",
            metadata={"db_path": target_db, "error_code": "DB_OPEN_FAILED"}
        )

    try:
        # 2. Schema inspection
        if op == "get_schema":
            if not table_name:
                # Return all tables and their columns
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
                tables = [r["name"] for r in cur.fetchall()]
                schema_info = {}
                for tbl in tables:
                    cur.execute(f"PRAGMA table_info({tbl});")
                    cols = [{"name": c["name"], "type": c["type"], "notnull": bool(c["notnull"]), "pk": bool(c["pk"])} for c in cur.fetchall()]
                    schema_info[tbl] = cols
                conn.close()
                return ToolResult.ok(
                    "database_tool",
                    data={"operation": "get_schema", "tables": schema_info},
                    metadata={"table_count": len(tables)}
                )
            else:
                cur.execute(f"PRAGMA table_info({table_name});")
                rows = cur.fetchall()
                conn.close()
                if not rows:
                    return ToolResult.fail(
                        "database_tool",
                        f"Table '{table_name}' does not exist in the database.",
                        metadata={"table_name": table_name}
                    )
                cols = [{"name": c["name"], "type": c["type"], "notnull": bool(c["notnull"]), "pk": bool(c["pk"])} for c in rows]
                return ToolResult.ok(
                    "database_tool",
                    data={"operation": "get_schema", "table_name": table_name, "columns": cols}
                )

        # 3. Read table
        elif op == "read_table":
            if not table_name:
                conn.close()
                return ToolResult.fail("database_tool", "Operation 'read_table' requires 'table_name' parameter.")

            # Validate table name against existing tables (anti-SQL-injection)
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
            if not cur.fetchone():
                conn.close()
                return ToolResult.fail("database_tool", f"Table '{table_name}' does not exist.")

            cur.execute(f"SELECT * FROM {table_name};")
            records = [dict(r) for r in cur.fetchall()]
            conn.close()
            return ToolResult.ok(
                "database_tool",
                data={
                    "operation": "read_table",
                    "table_name": table_name,
                    "record_count": len(records),
                    "records": records
                }
            )

        # 4. Custom parameterized query
        elif op == "query":
            if not query or not query.strip():
                conn.close()
                return ToolResult.fail("database_tool", "Operation 'query' requires a valid SQL query string.")

            clean_query = query.strip()
            # Guardrail: disallow destructive queries
            disallowed = ["drop", "truncate", "delete", "alter", "attach", "detach"]
            first_keyword = clean_query.split()[0].lower() if clean_query.split() else ""
            if first_keyword in disallowed or any(w in clean_query.lower() for w in ["drop table", "drop database"]):
                conn.close()
                return ToolResult.fail(
                    "database_tool",
                    f"Security restriction: Destructive SQL query ('{first_keyword.upper()}') is prohibited in read-only environment.",
                    metadata={"query": clean_query}
                )

            # Execute parameterized query
            cur.execute(clean_query, tuple(parameters))
            rows = cur.fetchall()
            records = [dict(r) for r in rows]
            conn.close()

            return ToolResult.ok(
                "database_tool",
                data={
                    "operation": "query",
                    "query": clean_query,
                    "parameters": parameters,
                    "record_count": len(records),
                    "records": records
                },
                metadata={"is_empty": len(records) == 0}
            )

        else:
            conn.close()
            return ToolResult.fail(
                "database_tool",
                f"Unsupported database operation '{operation}'. Allowed operations: 'query', 'read_table', 'get_schema'."
            )

    except sqlite3.OperationalError as oe:
        conn.close()
        return ToolResult.fail(
            "database_tool",
            f"SQLite OperationalError: {str(oe)}",
            metadata={"query": query, "error_code": "SQLITE_OPERATIONAL_ERROR"}
        )
    except sqlite3.DatabaseError as de:
        conn.close()
        return ToolResult.fail(
            "database_tool",
            f"SQLite DatabaseError: {str(de)}",
            metadata={"query": query, "error_code": "SQLITE_DATABASE_ERROR"}
        )
    except Exception as e:
        conn.close()
        return ToolResult.fail(
            "database_tool",
            f"Unexpected database failure: {str(e)}",
            metadata={"query": query}
        )


DATABASE_DEFINITION = ToolDefinition(
    name="database_tool",
    description="Queries local SQLite database ('company_records.db') with parameterized SQL, schema inspection, and error handling.",
    parameters={
        "operation": ToolParameter(
            name="operation",
            type="string",
            description="Database operation to perform.",
            required=True,
            enum=["query", "read_table", "get_schema"]
        ),
        "query": ToolParameter(
            name="query",
            type="string",
            description="SQL SELECT query string (required for 'query' operation).",
            required=False
        ),
        "table_name": ToolParameter(
            name="table_name",
            type="string",
            description="Name of the table to read or inspect (for 'read_table' and 'get_schema').",
            required=False
        ),
        "params": ToolParameter(
            name="params",
            type="array",
            description="Positional query parameters for parameterized queries.",
            required=False
        ),
        "db_path": ToolParameter(
            name="db_path",
            type="string",
            description="Optional custom path to SQLite database file.",
            required=False
        ),
        "simulate_connection_failure": ToolParameter(
            name="simulate_connection_failure",
            type="boolean",
            description="Flag for testing connection failure handling.",
            required=False,
            default=False
        )
    },
    returns={
        "type": "object",
        "properties": {
            "operation": {"type": "string"},
            "record_count": {"type": "integer"},
            "records": {"type": "array"}
        }
    },
    is_mock=False
)
