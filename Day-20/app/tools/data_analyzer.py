"""
Day 20 — Data Analyzer Tool
Computes statistical profiles, aggregations, column inspection,
and missing-value audits on structured datasets (CSV or JSON list of dicts).
Handles empty, malformed, non-numeric, and missing columns with robust error states.
"""

import os
import csv
import json
import io
from typing import Optional, List, Dict, Any, Union
from ..schemas import ToolResult, ToolDefinition, ToolParameter


def _load_data_records(
    data: Optional[Union[str, List[Dict[str, Any]]]],
    file_path: Optional[str]
) -> Union[List[Dict[str, Any]], str]:
    """
    Normalizes data source (direct records, CSV text, or file path) into list of row dicts.
    Returns list of dicts on success, or error string on failure.
    """
    if file_path:
        clean_path = file_path.strip()
        day20_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        repo_dir = os.path.dirname(day20_dir)
        cwd = os.getcwd()

        candidates = [
            clean_path if os.path.isabs(clean_path) else os.path.join(cwd, clean_path),
            os.path.join(day20_dir, "data", clean_path),
            os.path.join(day20_dir, clean_path),
            os.path.join(repo_dir, clean_path),
            os.path.join(day20_dir, "data", os.path.basename(clean_path)),
            os.path.join(repo_dir, "Day-20", "data", os.path.basename(clean_path))
        ]

        resolved = None
        for cand in candidates:
            if os.path.exists(cand):
                resolved = cand
                break

        if not resolved:
            return f"Dataset file not found: '{clean_path}'."
        clean_path = resolved

        try:
            with open(clean_path, "r", encoding="utf-8") as f:
                raw_text = f.read()
        except Exception as e:
            return f"Failed to read dataset file '{clean_path}': {str(e)}."

        if not raw_text.strip():
            return "Dataset file is completely empty."

        _, ext = os.path.splitext(clean_path)
        if ext.lower() == ".json":
            try:
                parsed = json.loads(raw_text)
                if not isinstance(parsed, list):
                    return "JSON dataset must be an array/list of record objects."
                return parsed
            except Exception as e:
                return f"Malformed JSON dataset: {str(e)}."
        else:
            # Default CSV parse
            try:
                reader = csv.DictReader(io.StringIO(raw_text))
                records = list(reader)
                if not records and reader.fieldnames is None:
                    return "Malformed or empty CSV file."
                return records
            except Exception as e:
                return f"Malformed CSV dataset: {str(e)}."

    elif data is not None:
        if isinstance(data, list):
            return data
        elif isinstance(data, str):
            clean_str = data.strip()
            if not clean_str:
                return "Dataset text string is empty."
            # Attempt JSON first
            if clean_str.startswith("["):
                try:
                    parsed = json.loads(clean_str)
                    if isinstance(parsed, list):
                        return parsed
                except Exception:
                    pass
            # Attempt CSV
            try:
                reader = csv.DictReader(io.StringIO(clean_str))
                records = list(reader)
                return records
            except Exception as e:
                return f"Malformed CSV string: {str(e)}."
        else:
            return f"Unsupported data input type: {type(data).__name__}."

    return "No dataset provided. Please supply either 'data' or 'file_path'."


def data_analyzer_tool(
    operation: str = "summary",
    data: Optional[Union[str, List[Dict[str, Any]]]] = None,
    file_path: Optional[str] = None,
    target_column: Optional[str] = None
) -> ToolResult:
    """
    Analyzes structured tabular/JSON datasets.
    Supported operations:
    - 'summary': Full statistical summary and profile.
    - 'row_count': Total number of records.
    - 'column_info': List of column names and observed types.
    - 'average': Mean value of specified target_column.
    - 'min_max': Minimum and maximum values of specified target_column.
    - 'missing_values': Count of null/empty values per column.
    """
    op = str(operation).strip().lower()

    # 1. Load records
    loaded = _load_data_records(data, file_path)
    if isinstance(loaded, str):
        return ToolResult.fail("data_analyzer", loaded, metadata={"operation": op})

    records = loaded
    if not records:
        return ToolResult.fail(
            "data_analyzer",
            "Dataset contains zero rows / records.",
            metadata={"operation": op, "error_code": "EMPTY_DATASET"}
        )

    # Extract all distinct column keys across records
    all_columns = list({k for row in records if isinstance(row, dict) for k in row.keys()})
    if not all_columns:
        return ToolResult.fail(
            "data_analyzer",
            "Dataset records contain no recognizable fields or columns.",
            metadata={"operation": op}
        )

    # 2. Row count operation
    if op == "row_count":
        return ToolResult.ok(
            "data_analyzer",
            data={"operation": "row_count", "row_count": len(records), "columns": all_columns}
        )

    # 3. Column info operation
    elif op == "column_info":
        col_types = {}
        for col in all_columns:
            observed_types = set()
            for r in records:
                val = r.get(col)
                if val is None or val == "":
                    observed_types.add("null")
                else:
                    # check if can be numeric float/int
                    try:
                        float(val)
                        observed_types.add("numeric")
                    except (ValueError, TypeError):
                        observed_types.add("string")
            col_types[col] = list(observed_types)

        return ToolResult.ok(
            "data_analyzer",
            data={
                "operation": "column_info",
                "total_columns": len(all_columns),
                "columns": all_columns,
                "inferred_types": col_types
            }
        )

    # 4. Missing values audit
    elif op == "missing_values":
        null_counts = {}
        for col in all_columns:
            null_count = sum(
                1 for r in records if r.get(col) is None or str(r.get(col)).strip() in ("", "null", "none", "nan")
            )
            null_counts[col] = {
                "missing_count": null_count,
                "missing_percentage": round((null_count / len(records)) * 100, 2)
            }

        return ToolResult.ok(
            "data_analyzer",
            data={
                "operation": "missing_values",
                "total_rows": len(records),
                "missing_audit": null_counts
            }
        )

    # 5. Average calculation
    elif op in ("average", "mean"):
        if not target_column:
            return ToolResult.fail("data_analyzer", "Operation 'average' requires 'target_column' parameter.")

        if target_column not in all_columns:
            return ToolResult.fail(
                "data_analyzer",
                f"Column '{target_column}' not found in dataset. Available columns: {all_columns}.",
                metadata={"target_column": target_column, "available_columns": all_columns}
            )

        numeric_vals = []
        non_numeric_count = 0
        for r in records:
            val = r.get(target_column)
            if val is None or str(val).strip() == "":
                continue
            try:
                numeric_vals.append(float(val))
            except (ValueError, TypeError):
                non_numeric_count += 1

        if not numeric_vals:
            return ToolResult.fail(
                "data_analyzer",
                f"Column '{target_column}' contains no numeric values to calculate average (non-numeric rows: {non_numeric_count}).",
                metadata={"target_column": target_column, "non_numeric_count": non_numeric_count}
            )

        avg_val = sum(numeric_vals) / len(numeric_vals)
        return ToolResult.ok(
            "data_analyzer",
            data={
                "operation": "average",
                "target_column": target_column,
                "average": round(avg_val, 4),
                "sample_size": len(numeric_vals),
                "ignored_non_numeric": non_numeric_count
            }
        )

    # 6. Min and Max
    elif op in ("min_max", "min", "max"):
        if not target_column:
            return ToolResult.fail("data_analyzer", "Operation 'min_max' requires 'target_column' parameter.")

        if target_column not in all_columns:
            return ToolResult.fail(
                "data_analyzer",
                f"Column '{target_column}' not found in dataset. Available columns: {all_columns}."
            )

        numeric_vals = []
        for r in records:
            val = r.get(target_column)
            if val is not None and str(val).strip() != "":
                try:
                    numeric_vals.append(float(val))
                except (ValueError, TypeError):
                    pass

        if not numeric_vals:
            return ToolResult.fail(
                "data_analyzer",
                f"Column '{target_column}' has no valid numeric values to determine min/max."
            )

        return ToolResult.ok(
            "data_analyzer",
            data={
                "operation": "min_max",
                "target_column": target_column,
                "minimum": min(numeric_vals),
                "maximum": max(numeric_vals),
                "range": round(max(numeric_vals) - min(numeric_vals), 4),
                "sample_size": len(numeric_vals)
            }
        )

    # 7. Comprehensive summary
    elif op == "summary":
        summary_stats = {}
        for col in all_columns:
            vals = [r.get(col) for r in records if r.get(col) is not None and str(r.get(col)).strip() != ""]
            num_vals = []
            for v in vals:
                try:
                    num_vals.append(float(v))
                except (ValueError, TypeError):
                    pass

            if num_vals and len(num_vals) >= len(vals) * 0.5:
                # Numeric column
                num_vals.sort()
                mean_val = sum(num_vals) / len(num_vals)
                summary_stats[col] = {
                    "type": "numeric",
                    "count": len(num_vals),
                    "mean": round(mean_val, 2),
                    "min": min(num_vals),
                    "max": max(num_vals)
                }
            else:
                summary_stats[col] = {
                    "type": "categorical",
                    "count": len(vals),
                    "distinct_values": len(set(str(v) for v in vals))
                }

        return ToolResult.ok(
            "data_analyzer",
            data={
                "operation": "summary",
                "total_rows": len(records),
                "total_columns": len(all_columns),
                "columns": all_columns,
                "column_statistics": summary_stats
            }
        )

    else:
        return ToolResult.fail(
            "data_analyzer",
            f"Unsupported data analysis operation '{operation}'. Supported operations: 'summary', 'row_count', 'column_info', 'average', 'min_max', 'missing_values'."
        )


DATA_ANALYZER_DEFINITION = ToolDefinition(
    name="data_analyzer",
    description="Analyzes structured tabular datasets (CSV/JSON): computes row counts, column types, averages, min/max, null audits, and summaries.",
    parameters={
        "operation": ToolParameter(
            name="operation",
            type="string",
            description="Analysis operation to execute.",
            required=False,
            default="summary",
            enum=["summary", "row_count", "column_info", "average", "min_max", "missing_values"]
        ),
        "data": ToolParameter(
            name="data",
            type="object",
            description="Inline data records (JSON list of dicts or CSV string).",
            required=False
        ),
        "file_path": ToolParameter(
            name="file_path",
            type="string",
            description="Path to CSV or JSON file on disk.",
            required=False
        ),
        "target_column": ToolParameter(
            name="target_column",
            type="string",
            description="Specific column name required for 'average' and 'min_max' operations.",
            required=False
        )
    },
    returns={
        "type": "object",
        "properties": {
            "operation": {"type": "string"},
            "data": {"type": "object"}
        }
    },
    is_mock=False
)
