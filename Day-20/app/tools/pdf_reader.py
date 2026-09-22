"""
Day 20 — PDF Reader Tool (Project Practical Tool)
Provides dynamic text extraction, page-level inspection, keyword search,
and metadata extraction from PDF documents using pypdf.
"""

import os
import re
from typing import Dict, Any, Optional, List
from ..schemas import ToolResult, ToolDefinition, ToolParameter


ALLOWED_EXTENSIONS = {".pdf"}


def _resolve_and_validate_path(file_path: str) -> Optional[str]:
    """Resolves relative or absolute path and checks existence within project sandbox."""
    if not file_path or not file_path.strip():
        return None

    clean_path = file_path.strip().replace("\\", "/")
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(base_dir, "data")

    candidates = [
        os.path.join(data_dir, os.path.basename(clean_path)),
        os.path.join(base_dir, clean_path),
        os.path.abspath(clean_path)
    ]

    for candidate in candidates:
        if os.path.exists(candidate) and os.path.isfile(candidate):
            return os.path.abspath(candidate)

    return os.path.abspath(candidates[0])


def pdf_reader_tool(
    file_path: str,
    page_number: Optional[int] = None,
    search_keyword: Optional[str] = None,
    max_pages: int = 10,
    operation: Optional[str] = None,
    keyword: Optional[str] = None,
    **kwargs: Any
) -> ToolResult:
    """
    Reads and inspects PDF documents:
    - Extracts full text or specific page text.
    - Inspects metadata (author, title, page count).
    - Searches for keywords across all pages.
    """
    try:
        import pypdf
    except ImportError:
        return ToolResult.fail("pdf_reader", "Missing dependency 'pypdf'. Please install via pip.")

    if not file_path or not file_path.strip():
        return ToolResult.fail("pdf_reader", "Parameter 'file_path' cannot be empty.")

    if keyword and not search_keyword:
        search_keyword = keyword

    resolved = _resolve_and_validate_path(file_path)
    if not resolved or not os.path.exists(resolved):
        return ToolResult.fail(
            "pdf_reader",
            f"PDF file not found: '{file_path}'. Please verify the file path.",
            metadata={"file_path": file_path, "error_code": "FILE_NOT_FOUND"}
        )

    ext = os.path.splitext(resolved)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return ToolResult.fail(
            "pdf_reader",
            f"Invalid file extension '{ext}'. Only .pdf files are supported by pdf_reader.",
            metadata={"file_path": file_path, "error_code": "UNSUPPORTED_FORMAT"}
        )

    try:
        reader = pypdf.PdfReader(resolved)
        total_pages = len(reader.pages)
        meta = reader.metadata or {}

        metadata_dict = {
            "title": getattr(meta, "title", None) or os.path.basename(resolved),
            "author": getattr(meta, "author", None) or "Unknown",
            "page_count": total_pages,
            "filename": os.path.basename(resolved),
            "file_size_bytes": os.path.getsize(resolved)
        }

        # Page-specific reading
        if page_number is not None:
            if page_number < 1 or page_number > total_pages:
                return ToolResult.fail(
                    "pdf_reader",
                    f"Invalid page_number {page_number}. PDF contains {total_pages} pages.",
                    metadata={"total_pages": total_pages}
                )
            page_idx = page_number - 1
            text = reader.pages[page_idx].extract_text() or ""
            return ToolResult.ok(
                "pdf_reader",
                data={
                    "filename": os.path.basename(resolved),
                    "page_number": page_number,
                    "total_pages": total_pages,
                    "page_text": text.strip(),
                    "char_count": len(text),
                    "word_count": len(text.split()),
                    "metadata": metadata_dict
                }
            )

        # In-document keyword search
        if search_keyword and search_keyword.strip():
            kw = search_keyword.strip().lower()
            matching_pages = []
            for idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                if kw in page_text.lower():
                    # Extract brief matching snippet
                    m = re.search(r"([^.\n]{0,50}" + re.escape(kw) + r"[^.\n]{0,50})", page_text, re.IGNORECASE)
                    snippet = m.group(0).strip() if m else kw
                    matching_pages.append({
                        "page": idx + 1,
                        "snippet": f"...{snippet}..."
                    })

            return ToolResult.ok(
                "pdf_reader",
                data={
                    "filename": os.path.basename(resolved),
                    "search_keyword": search_keyword.strip(),
                    "matches_found": len(matching_pages),
                    "matching_pages": matching_pages,
                    "metadata": metadata_dict
                }
            )

        # Default: Full or truncated document extraction
        pages_to_extract = min(total_pages, max_pages)
        extracted_pages = []
        full_text_parts = []
        for idx in range(pages_to_extract):
            t = reader.pages[idx].extract_text() or ""
            full_text_parts.append(t)
            extracted_pages.append({
                "page": idx + 1,
                "text": t.strip(),
                "word_count": len(t.split())
            })

        combined_text = "\n\n".join(full_text_parts)
        return ToolResult.ok(
            "pdf_reader",
            data={
                "filename": os.path.basename(resolved),
                "total_pages": total_pages,
                "extracted_pages_count": pages_to_extract,
                "pages": extracted_pages,
                "summary_preview": combined_text[:300] + ("..." if len(combined_text) > 300 else ""),
                "metadata": metadata_dict
            }
        )

    except Exception as e:
        return ToolResult.fail(
            "pdf_reader",
            f"Error processing PDF file '{os.path.basename(resolved)}': {str(e)}",
            metadata={"file_path": file_path}
        )


PDF_READER_DEFINITION = ToolDefinition(
    name="pdf_reader",
    description="Extracts text, metadata, and searches keywords across PDF documents dynamically.",
    parameters={
        "file_path": ToolParameter(
            name="file_path",
            type="string",
            description="Path to the PDF file (e.g. 'company_handbook.pdf').",
            required=True
        ),
        "page_number": ToolParameter(
            name="page_number",
            type="integer",
            description="Specific 1-indexed page number to extract text from.",
            required=False
        ),
        "search_keyword": ToolParameter(
            name="search_keyword",
            type="string",
            description="Keyword to search for across all pages in the PDF document.",
            required=False
        ),
        "keyword": ToolParameter(
            name="keyword",
            type="string",
            description="Alias for search_keyword.",
            required=False
        ),
        "operation": ToolParameter(
            name="operation",
            type="string",
            description="Operation mode ('read_all', 'read_page', 'get_metadata', 'search').",
            required=False,
            default="read_all"
        ),
        "max_pages": ToolParameter(
            name="max_pages",
            type="integer",
            description="Maximum number of pages to extract in multi-page mode (default 10).",
            required=False,
            default=10
        )
    },
    returns={
        "type": "object",
        "properties": {
            "filename": {"type": "string"},
            "total_pages": {"type": "integer"},
            "metadata": {"type": "object"}
        }
    },
    is_mock=False
)
