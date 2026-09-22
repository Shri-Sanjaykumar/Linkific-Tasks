"""
Day 20 — Company Project Practical Tool: Company Search & Policy Retrieval Tool
Section 8 Deliverable: Integrates with Linkific's existing document knowledge base (Days 16-19),
providing structured keyword search, section parsing, category filtering, and policy verification.
"""

import os
import re
from typing import Optional, List, Dict, Any
from ..schemas import ToolResult, ToolDefinition, ToolParameter


def _find_company_policy_files() -> List[str]:
    """Discovers synthetic organizational documents across Day-20, Day-19, and Day-18 data dirs."""
    found = []
    base_cur = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    day20_data = os.path.join(base_cur, "data")
    if os.path.exists(day20_data):
        for f in os.listdir(day20_data):
            if f.endswith(".txt"):
                found.append(os.path.join(day20_data, f))

    # Also search adjacent Day-19/data if available
    day19_data = os.path.join(os.path.dirname(base_cur), "Day-19", "data")
    if os.path.exists(day19_data):
        for f in os.listdir(day19_data):
            if f.endswith(".txt"):
                found.append(os.path.join(day19_data, f))

    return found


def company_search_tool(
    query: str,
    category: Optional[str] = None,
    top_k: int = 3
) -> ToolResult:
    """
    Searches Linkific synthetic organizational policies, onboarding documents,
    and workflow specifications for matching guidelines and sections.
    """
    # 1. Validation
    if not query or not query.strip():
        return ToolResult.fail("company_search", "Company search query cannot be empty or whitespace.")

    clean_query = query.strip()
    query_tokens = [w.lower() for w in re.findall(r"\b[a-zA-Z0-9_-]{2,}\b", clean_query)]

    # 2. Locate documents
    doc_paths = _find_company_policy_files()
    if not doc_paths:
        return ToolResult.fail(
            "company_search",
            "No organizational documentation files found in local repository data directories.",
            metadata={"query": clean_query, "error_code": "NO_DOCS_FOUND"}
        )

    matches = []

    for path in doc_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            continue

        fname = os.path.basename(path)
        doc_id = "DOC-GENERAL"
        doc_title = fname
        doc_category = "General"

        # Parse header metadata if present
        for line in content.splitlines()[:12]:
            if line.startswith("DOCUMENT ID:"):
                doc_id = line.replace("DOCUMENT ID:", "").strip()
            elif line.startswith("DOCUMENT TITLE:"):
                doc_title = line.replace("DOCUMENT TITLE:", "").strip()
            elif line.startswith("CATEGORY:"):
                doc_category = line.replace("CATEGORY:", "").strip()

        # Category filter check
        if category and category.strip().lower() not in doc_category.lower():
            continue

        # Split into numbered sections or paragraphs
        sections = [s.strip() for s in re.split(r"\n\s*(?=[0-9]+\.|\={3,})", content) if len(s.strip()) > 30]

        for s_idx, sec in enumerate(sections):
            # Compute term overlap score
            sec_lower = sec.lower()
            matched_terms = [t for t in query_tokens if t in sec_lower]
            overlap_score = len(matched_terms) / max(len(query_tokens), 1)

            if overlap_score > 0:
                first_line = sec.splitlines()[0][:60]
                matches.append({
                    "document_id": doc_id,
                    "title": doc_title,
                    "category": doc_category,
                    "section_index": s_idx + 1,
                    "heading": first_line,
                    "excerpt": sec[:250] + ("..." if len(sec) > 250 else ""),
                    "relevance_score": round(overlap_score, 3),
                    "source_file": fname
                })

    # Sort descending by relevance
    matches.sort(key=lambda x: x["relevance_score"], reverse=True)
    top_matches = matches[:top_k]

    if not top_matches:
        return ToolResult.ok(
            "company_search",
            data={
                "query": clean_query,
                "category_filter": category,
                "matches_count": 0,
                "matches": [],
                "message": f"No matching organizational policies or guidelines found for '{clean_query}'."
            },
            metadata={"status": "no_match"}
        )

    return ToolResult.ok(
        "company_search",
        data={
            "query": clean_query,
            "category_filter": category,
            "matches_count": len(top_matches),
            "matches": top_matches
        },
        metadata={"total_candidates": len(matches)}
    )


COMPANY_SEARCH_DEFINITION = ToolDefinition(
    name="company_search",
    description="Searches Linkific organizational policy guidelines, leave rules, remote work terms, and onboarding documents.",
    parameters={
        "query": ToolParameter(
            name="query",
            type="string",
            description="Policy, rule, or topic query (e.g., 'leave entitlement', 'core hours', 'remote work allowance').",
            required=True
        ),
        "category": ToolParameter(
            name="category",
            type="string",
            description="Optional category filter (e.g., 'Corporate Policy', 'Leave', 'Onboarding').",
            required=False
        ),
        "top_k": ToolParameter(
            name="top_k",
            type="integer",
            description="Maximum number of relevant policy sections to return.",
            required=False,
            default=3
        )
    },
    returns={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "matches_count": {"type": "integer"},
            "matches": {"type": "array"}
        }
    },
    is_mock=False
)
