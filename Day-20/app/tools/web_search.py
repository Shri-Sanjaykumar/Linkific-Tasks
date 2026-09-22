"""
Day 20 — Web Search Tool
Simulated web search engine over a curated demonstration index.
Clearly labeled as a local demonstration (external search API unconfigured).
"""

from typing import Optional, List, Dict, Any
from ..schemas import ToolResult, ToolDefinition, ToolParameter


# Local demonstration web index for common technical and domain queries
MOCK_WEB_INDEX: List[Dict[str, str]] = [
    {
        "title": "LangGraph: Building Stateful Multi-Actor Applications with LLMs",
        "url": "https://langchain-ai.github.io/langgraph/",
        "snippet": "LangGraph is a library for building stateful, multi-actor applications with LLMs, used to create agent and multi-agent workflows with cyclic graph structures.",
        "keywords": ["langgraph", "agent", "stateful", "graph", "llm", "workflow"]
    },
    {
        "title": "Python Function Calling and Tool Use Overview",
        "url": "https://docs.python.org/3/library/inspect.html",
        "snippet": "Function calling allows models and agents to select tools, produce structured arguments, and execute deterministic APIs safely with argument validation.",
        "keywords": ["python", "function calling", "tool", "tools", "arguments", "api"]
    },
    {
        "title": "FastAPI: Modern, Fast Web Framework for Python",
        "url": "https://fastapi.tiangolo.com/",
        "snippet": "FastAPI is a high-performance web framework for building APIs with Python 3.8+ based on standard Python type hints and Pydantic data validation.",
        "keywords": ["fastapi", "api", "rest", "pydantic", "microservice"]
    },
    {
        "title": "Sentence-Transformers: Multilingual Sentence, Text & Image Embeddings",
        "url": "https://sbert.net/",
        "snippet": "SentenceTransformers is a Python framework for state-of-the-art sentence, text and image embeddings, supporting semantic search and dense retrieval.",
        "keywords": ["sentence-transformers", "embeddings", "rag", "dense", "vector", "search"]
    },
    {
        "title": "Linkific Internship Technical Curriculum Overview",
        "url": "https://linkific.internal/curriculum",
        "snippet": "Linkific AI/ML internship syllabus covering NLP, embeddings, vector databases, FastAPI RAG microservices, ReAct AI agents, LangGraph workflows, and tool creation.",
        "keywords": ["linkific", "internship", "curriculum", "syllabus", "tasks"]
    },
    {
        "title": "PyTorch: Deep Learning Framework and Tensors",
        "url": "https://pytorch.org/",
        "snippet": "PyTorch is an optimized tensor library for deep learning using GPUs and CPUs with dynamic computational graphs.",
        "keywords": ["pytorch", "deep learning", "neural network", "ai", "tensors", "gpu"]
    },
    {
        "title": "Scikit-Learn: Machine Learning in Python",
        "url": "https://scikit-learn.org/",
        "snippet": "Simple and efficient tools for predictive data analysis, accessible to everybody, and reusable in various contexts built on NumPy, SciPy, and matplotlib.",
        "keywords": ["scikit-learn", "sklearn", "machine learning", "classification", "regression", "clustering"]
    },
    {
        "title": "Pandas: Data Analysis and Manipulation Library",
        "url": "https://pandas.pydata.org/",
        "snippet": "Pandas is a fast, powerful, flexible and easy to use open source data analysis and data manipulation tool, built on top of the Python programming language.",
        "keywords": ["pandas", "dataframe", "data analysis", "csv", "tabular", "data"]
    }
]


def _fetch_live_web_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Fetches real live search results using Wikipedia and DuckDuckGo search endpoints."""
    import requests
    import re
    results = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

    # Source 1: Wikipedia Search API
    try:
        wiki_url = "https://en.wikipedia.org/w/api.php"
        resp = requests.get(
            wiki_url,
            params={"action": "query", "list": "search", "srsearch": query, "format": "json", "srlimit": max_results},
            headers=headers,
            timeout=3.0
        )
        if resp.status_code == 200:
            data = resp.json()
            search_items = data.get("query", {}).get("search", [])
            for idx, item in enumerate(search_items):
                raw_snippet = item.get("snippet", "")
                clean_snippet = re.sub(r"<[^>]+>", "", raw_snippet)
                title = item.get("title", "")
                page_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
                results.append({
                    "title": title,
                    "url": page_url,
                    "snippet": clean_snippet or f"Technical reference article on {title}",
                    "relevance_score": round(max(0.95 - (idx * 0.1), 0.5), 2),
                    "source": "Wikipedia Online Search"
                })
    except Exception:
        pass

    # Source 2: DuckDuckGo Instant Answer API if results are few
    if len(results) < max_results:
        try:
            ddg_url = "https://api.duckduckgo.com/"
            resp = requests.get(
                ddg_url,
                params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
                headers=headers,
                timeout=3.0
            )
            if resp.status_code == 200:
                ddg_data = resp.json()
                if ddg_data.get("Abstract"):
                    results.insert(0, {
                        "title": ddg_data.get("Heading") or query.title(),
                        "url": ddg_data.get("AbstractURL") or f"https://duckduckgo.com/?q={query}",
                        "snippet": ddg_data.get("Abstract"),
                        "relevance_score": 0.98,
                        "source": "DuckDuckGo Instant Knowledge"
                    })
                for rel in ddg_data.get("RelatedTopics", [])[:max_results - len(results)]:
                    if isinstance(rel, dict) and rel.get("Text"):
                        results.append({
                            "title": rel.get("Text")[:60] + "...",
                            "url": rel.get("FirstURL") or f"https://duckduckgo.com/?q={query}",
                            "snippet": rel.get("Text"),
                            "relevance_score": 0.85,
                            "source": "DuckDuckGo Topic Index"
                        })
        except Exception:
            pass

    return results[:max_results]


def web_search_tool(
    query: str,
    max_results: int = 5,
    simulate_service_failure: bool = False
) -> ToolResult:
    """
    Performs web search dynamically via live web endpoints (Wikipedia & DuckDuckGo),
    with automatic offline fallback to local technical index.
    """
    # 1. Empty query validation
    if not query or not query.strip():
        return ToolResult.fail(
            "web_search",
            "Search query cannot be empty or whitespace.",
            metadata={"query": query}
        )

    clean_query = query.strip()

    # 2. Simulated service failure handling
    if simulate_service_failure:
        return ToolResult.fail(
            "web_search",
            "Upstream search provider timeout (HTTP 503 Service Unavailable).",
            metadata={
                "query": clean_query,
                "error_code": "UPSTREAM_SERVICE_TIMEOUT",
                "is_mock": True
            }
        )

    # 3. Attempt live online search first
    live_results = _fetch_live_web_search(clean_query, max_results)
    if live_results:
        return ToolResult.ok(
            "web_search",
            data={
                "query": clean_query,
                "total_results": len(live_results),
                "results": live_results
            },
            metadata={
                "is_live": True,
                "provider": "Live Web Search (Wikipedia & DuckDuckGo)"
            }
        )

    # 4. Fallback to curated technical index if offline or unreachable
    query_terms = [term.lower() for term in clean_query.split() if len(term) > 1]
    matches = []

    for doc in MOCK_WEB_INDEX:
        score = 0
        doc_text = (doc["title"] + " " + doc["snippet"] + " " + " ".join(doc["keywords"])).lower()
        for term in query_terms:
            if term in doc_text:
                score += 1

        if score > 0 or not query_terms:
            matches.append({
                "title": doc["title"],
                "url": doc["url"],
                "snippet": doc["snippet"],
                "relevance_score": round(score / max(len(query_terms), 1), 2)
            })

    # Sort descending by relevance
    matches.sort(key=lambda x: x["relevance_score"], reverse=True)
    results = matches[:max_results]

    return ToolResult.ok(
        "web_search",
        data={
            "query": clean_query,
            "total_results": len(results),
            "results": results
        },
        metadata={
            "is_live": False,
            "provider": "Curated Local Technical Offline Index"
        }
    )


WEB_SEARCH_DEFINITION = ToolDefinition(
    name="web_search",
    description="Searches live online web resources and technical documentation for a given query, with offline fallback.",
    parameters={
        "query": ToolParameter(
            name="query",
            type="string",
            description="The search terms or question to look up.",
            required=True
        ),
        "max_results": ToolParameter(
            name="max_results",
            type="integer",
            description="Maximum number of search results to return.",
            required=False,
            default=5
        ),
        "simulate_service_failure": ToolParameter(
            name="simulate_service_failure",
            type="boolean",
            description="Flag for testing service failure and error handling.",
            required=False,
            default=False
        )
    },
    returns={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "total_results": {"type": "integer"},
            "results": {"type": "array"}
        }
    },
    is_mock=True,
    mock_notice="Live online search with local fallback index."
)
