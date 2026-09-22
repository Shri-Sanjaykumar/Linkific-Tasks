"""
Day 20 — File Reader Tool
Safely reads local files in supported formats (.txt, .json, .csv, .md),
validates file existence, enforces extension whitelisting, prevents directory traversal,
and returns structured text, parseable representations, and metadata.
"""

import os
import json
import csv
import io
from typing import Optional, Dict, Any, List
from ..schemas import ToolResult, ToolDefinition, ToolParameter


SUPPORTED_EXTENSIONS = {".txt", ".json", ".csv", ".md"}


def _resolve_and_validate_path(file_path: str):
    """
    Safely resolves relative or absolute file paths across local project data directories.
    Blocks genuine directory traversal attempts (e.g. escaping to root/system directories).
    Returns (resolved_path, error_message, error_code).
    """
    clean_path = file_path.strip()
    day20_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    repo_dir = os.path.dirname(day20_dir)
    cwd = os.getcwd()

    allowed_roots = [
        os.path.realpath(os.path.abspath(day20_dir)),
        os.path.realpath(os.path.abspath(repo_dir)),
        os.path.realpath(os.path.abspath(cwd))
    ]

    # Pre-check for explicit directory traversal attacks (escaping outside project workspace)
    target_abs = os.path.realpath(os.path.abspath(clean_path))
    target_abs_day20 = os.path.realpath(os.path.abspath(os.path.join(day20_dir, clean_path)))
    if not any(target_abs.startswith(root) for root in allowed_roots) and not any(target_abs_day20.startswith(root) for root in allowed_roots):
        return None, f"Security policy violation: Path '{clean_path}' escapes the authorized project workspace.", "PATH_TRAVERSAL_BLOCKED"

    # Candidate resolution paths
    candidates = [
        clean_path if os.path.isabs(clean_path) else os.path.join(cwd, clean_path),
        os.path.join(day20_dir, "data", clean_path),
        os.path.join(day20_dir, clean_path),
        os.path.join(repo_dir, clean_path),
        os.path.join(repo_dir, "Day-20", "data", clean_path),
        os.path.join(repo_dir, "Day-20", clean_path)
    ]

    resolved = None
    for cand in candidates:
        if os.path.exists(cand):
            resolved = cand
            break

    if not resolved:
        return None, f"File not found: '{clean_path}'. Please check the path and try again.", "FILE_NOT_FOUND"

    resolved_abs = os.path.realpath(os.path.abspath(resolved))
    if not any(resolved_abs.startswith(root) for root in allowed_roots):
        return None, f"Security policy violation: Path '{clean_path}' escapes the authorized project workspace.", "PATH_TRAVERSAL_BLOCKED"

    return resolved_abs, None, None


def file_reader_tool(
    file_path: str,
    max_chars: Optional[int] = None,
    encoding: str = "utf-8"
) -> ToolResult:
    """
    Reads local files in supported formats (.txt, .json, .csv, .md) and returns structured metadata.
    """
    if not file_path or not file_path.strip():
        return ToolResult.fail("file_reader", "File path cannot be empty.")

    clean_path = file_path.strip()

    # 1. Path resolution and workspace safety validation
    resolved_path, err_msg, err_code = _resolve_and_validate_path(clean_path)
    if err_msg:
        return ToolResult.fail(
            "file_reader",
            err_msg,
            metadata={"file_path": clean_path, "error_code": err_code}
        )

    clean_path = resolved_path

    if os.path.isdir(clean_path):
        return ToolResult.fail(
            "file_reader",
            f"Target path '{clean_path}' is a directory, not a readable file.",
            metadata={"file_path": clean_path, "error_code": "IS_A_DIRECTORY"}
        )

    # 2. Extension validation
    _, ext = os.path.splitext(clean_path)
    ext_lower = ext.lower()
    if ext_lower not in SUPPORTED_EXTENSIONS:
        return ToolResult.fail(
            "file_reader",
            f"Unsupported file format '{ext}'. Allowed extensions: {sorted(list(SUPPORTED_EXTENSIONS))}.",
            metadata={"file_path": clean_path, "extension": ext, "error_code": "UNSUPPORTED_FORMAT"}
        )

    # 3. Read content with encoding protection
    try:
        with open(clean_path, "r", encoding=encoding, errors="strict") as f:
            raw_content = f.read()
    except UnicodeDecodeError as ude:
        return ToolResult.fail(
            "file_reader",
            f"Encoding error while reading '{clean_path}' with '{encoding}': {str(ude)}.",
            metadata={"file_path": clean_path, "error_code": "ENCODING_ERROR"}
        )
    except Exception as e:
        return ToolResult.fail(
            "file_reader",
            f"Failed to read file '{clean_path}': {str(e)}.",
            metadata={"file_path": clean_path, "error_code": "READ_FAILURE"}
        )

    # Apply character limit if specified
    content_to_return = raw_content[:max_chars] if max_chars is not None else raw_content
    char_count = len(raw_content)
    line_count = len(raw_content.splitlines())
    file_size_bytes = os.path.getsize(clean_path)

    parsed_data = None
    if ext_lower == ".json":
        try:
            parsed_data = json.loads(raw_content)
        except Exception:
            parsed_data = None
    elif ext_lower == ".csv":
        try:
            reader = csv.DictReader(io.StringIO(raw_content))
            parsed_data = list(reader)
        except Exception:
            parsed_data = None

    return ToolResult.ok(
        "file_reader",
        data={
            "file_path": clean_path,
            "filename": os.path.basename(clean_path),
            "extension": ext_lower,
            "char_count": char_count,
            "line_count": line_count,
            "file_size_bytes": file_size_bytes,
            "content": content_to_return,
            "parsed_structure": parsed_data,
            "truncated": (max_chars is not None and char_count > max_chars)
        },
        metadata={"encoding": encoding}
    )


FILE_READER_DEFINITION = ToolDefinition(
    name="file_reader",
    description="Reads local files (.txt, .csv, .json, .md) with path safety checks, encoding handling, and metadata parsing.",
    parameters={
        "file_path": ToolParameter(
            name="file_path",
            type="string",
            description="Absolute or relative path to the file to read.",
            required=True
        ),
        "max_chars": ToolParameter(
            name="max_chars",
            type="integer",
            description="Maximum number of characters to return (truncation guard).",
            required=False
        ),
        "encoding": ToolParameter(
            name="encoding",
            type="string",
            description="Text encoding (default 'utf-8').",
            required=False,
            default="utf-8"
        )
    },
    returns={
        "type": "object",
        "properties": {
            "file_path": {"type": "string"},
            "content": {"type": "string"},
            "char_count": {"type": "integer"},
            "line_count": {"type": "integer"},
            "parsed_structure": {"type": "object"}
        }
    },
    is_mock=False
)
