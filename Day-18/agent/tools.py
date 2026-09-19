"""
Day 18 — AI Agent Tools Module
Implements four discrete, verifiable tools:
1. document_search: Lexical relevance / term-overlap search over synthetic knowledge base
2. document_lookup: Direct document retrieval by document ID
3. document_metadata: Metadata inspector (author, version, category, char count)
4. final_response: Grounded answer synthesis with source document attribution
"""

import os
import re
from typing import List, Dict, Any, Optional
from .schemas import SearchResult, DocumentMetadata, ToolResult


class KnowledgeBaseLoader:
    """Loads and caches synthetic knowledge base files from Day-18/data/."""

    _documents_cache: Dict[str, str] = {}
    _metadata_cache: Dict[str, DocumentMetadata] = {}

    @classmethod
    def get_data_dir(cls) -> str:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, "data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
        return data_dir

    @classmethod
    def load_all(cls) -> Dict[str, str]:
        if cls._documents_cache:
            return cls._documents_cache

        data_dir = cls.get_data_dir()
        if not os.path.exists(data_dir):
            return {}

        for fname in os.listdir(data_dir):
            if fname.endswith(".txt"):
                fpath = os.path.join(data_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()
                        cls._documents_cache[fname] = content
                        cls._parse_metadata(fname, content)
                except Exception as e:
                    print(f"Warning: Could not read {fname}: {e}")

        return cls._documents_cache

    @classmethod
    def _parse_metadata(cls, fname: str, text: str):
        doc_id = "DOC-UNKNOWN"
        title = fname
        category = "General"
        author = "Linkific Team"
        version = "1.0"

        for line in text.splitlines()[:15]:
            if line.startswith("DOCUMENT ID:"):
                doc_id = line.replace("DOCUMENT ID:", "").strip()
            elif line.startswith("DOCUMENT TITLE:"):
                title = line.replace("DOCUMENT TITLE:", "").strip()
            elif line.startswith("CATEGORY:"):
                category = line.replace("CATEGORY:", "").strip()
            elif line.startswith("AUTHOR:"):
                author = line.replace("AUTHOR:", "").strip()
            elif line.startswith("VERSION:"):
                version = line.replace("VERSION:", "").strip()

        paragraphs = [p for p in text.split("\n\n") if len(p.strip()) > 30]
        meta = DocumentMetadata(
            document_id=doc_id,
            title=title,
            category=category,
            author=author,
            version=version,
            char_count=len(text),
            chunk_count=len(paragraphs)
        )
        cls._metadata_cache[doc_id.upper()] = meta

    @classmethod
    def get_documents(cls) -> Dict[str, str]:
        return cls.load_all()

    @classmethod
    def get_metadata_by_id(cls, doc_id: str) -> Optional[DocumentMetadata]:
        cls.load_all()
        return cls._metadata_cache.get(doc_id.strip().upper())

    @classmethod
    def get_document_by_id(cls, doc_id: str) -> Optional[Dict[str, Any]]:
        docs = cls.load_all()
        doc_id_clean = doc_id.strip().upper()
        for fname, text in docs.items():
            if doc_id_clean in text.upper():
                meta = cls._metadata_cache.get(doc_id_clean)
                return {
                    "document_id": doc_id_clean,
                    "title": meta.title if meta else fname,
                    "category": meta.category if meta else "General",
                    "content": text
                }
        return None


# ------------------------------------------------------------------------------
# TOOL 1: document_search(query, top_k)
# ------------------------------------------------------------------------------
def document_search(query: str, top_k: int = 3) -> List[SearchResult]:
    """
    Search the synthetic knowledge base for chunks relevant to the query.
    Uses tokenized term-frequency lexical overlap scoring against substantive keywords.
    (Note: Dense vector retrieval from Day 16 is a proposed future integration).
    """
    docs = KnowledgeBaseLoader.load_all()
    if not query or not query.strip() or not docs:
        return []

    STOP_WORDS = {
        "what", "is", "the", "a", "an", "and", "or", "in", "on", "at", "for",
        "to", "of", "with", "by", "are", "about", "how", "do", "does", "can",
        "tell", "me", "this", "that", "it", "its", "company", "linkific", "there"
    }

    q_lower = query.lower()
    raw_tokens = set(re.findall(r"[a-zA-Z0-9]+", q_lower))
    substantive_tokens = raw_tokens - STOP_WORDS
    q_tokens = substantive_tokens if substantive_tokens else raw_tokens

    if not q_tokens:
        return []

    scored_chunks: List[SearchResult] = []

    for fname, text in docs.items():
        meta = None
        for m in KnowledgeBaseLoader._metadata_cache.values():
            if m.document_id in text:
                meta = m
                break
        doc_id = meta.document_id if meta else "DOC-UNKNOWN"
        doc_title = meta.title if meta else fname

        paragraphs = text.split("\n\n")
        current_offset = 0

        for p in paragraphs:
            p_strip = p.strip()
            p_len = len(p)
            if len(p_strip) < 30:
                current_offset += p_len + 2
                continue

            p_lower = p_strip.lower()
            p_tokens = set(re.findall(r"[a-zA-Z0-9]+", p_lower))

            matches = q_tokens.intersection(p_tokens)
            if matches:
                # Substantive term overlap ratio
                base_score = len(matches) / len(q_tokens)

                # Bonus for exact query phrase containment
                if query.lower() in p_lower:
                    base_score += 0.35

                # Bonus if substantive query tokens appear in title
                title_matches = q_tokens.intersection(set(re.findall(r"[a-zA-Z0-9]+", doc_title.lower())))
                if title_matches:
                    base_score += 0.20 * (len(title_matches) / len(q_tokens))

                relevance = round(min(1.0, base_score), 4)
                if relevance >= 0.25:
                    scored_chunks.append(
                        SearchResult(
                            document_id=doc_id,
                            document_title=doc_title,
                            matched_text=p_strip,
                            relevance_score=relevance,
                            char_start=current_offset,
                            char_end=current_offset + len(p_strip)
                        )
                    )
            current_offset += p_len + 2

    # Sort descending by relevance score
    scored_chunks.sort(key=lambda x: x.relevance_score, reverse=True)
    return scored_chunks[:top_k]


# ------------------------------------------------------------------------------
# TOOL 2: document_lookup(document_id)
# ------------------------------------------------------------------------------
def document_lookup(document_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve an entire document when the agent knows the specific document ID."""
    return KnowledgeBaseLoader.get_document_by_id(document_id)


# ------------------------------------------------------------------------------
# TOOL 3: document_metadata(document_id)
# ------------------------------------------------------------------------------
def document_metadata(document_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve author, category, version, and character counts for a document ID."""
    meta = KnowledgeBaseLoader.get_metadata_by_id(document_id)
    return meta.model_dump() if meta else None


# ------------------------------------------------------------------------------
# TOOL 4: final_response(context, question)
# ------------------------------------------------------------------------------
def final_response(context: str, question: str) -> Dict[str, Any]:
    """
    Synthesizes a grounded final response using retrieved context.
    If context is empty or missing, safely signals lack of information.
    """
    if not context or not context.strip():
        return {
            "answer": f"I could not find relevant information answering '{question}' in the available demonstration knowledge base.",
            "status": "no_relevant_information"
        }

    # If context is a metadata string representation, format neatly
    if context.startswith("{") and "document_id" in context:
        import ast
        try:
            m_dict = ast.literal_eval(context)
            formatted = (
                f"Document ID: {m_dict.get('document_id')}, "
                f"Title: '{m_dict.get('title')}', "
                f"Author: '{m_dict.get('author')}', "
                f"Version: '{m_dict.get('version')}', "
                f"Category: '{m_dict.get('category')}', "
                f"Character Count: {m_dict.get('char_count')}, "
                f"Chunk Count: {m_dict.get('chunk_count')}."
            )
            return {
                "answer": f"Based on the demonstration documentation: {formatted}",
                "status": "answered"
            }
        except Exception:
            pass

    lines = [line.strip() for line in context.splitlines() if line.strip()]
    content_lines = []
    for line in lines:
        if any(line.startswith(h) for h in ["===", "DOCUMENT ID:", "CATEGORY:", "AUTHOR:", "VERSION:", "NOTICE:"]):
            continue
        content_lines.append(line)

    substantive_text = " ".join(content_lines)
    sentences = re.split(r"(?<=[.!?])\s+", substantive_text)

    q_words = set(re.findall(r"[a-zA-Z0-9]+", question.lower())) - {
        "what", "is", "the", "a", "an", "and", "or", "in", "on", "at", "for", "to"
    }

    relevant_sentences = []
    for s in sentences:
        s_clean = s.strip()
        if len(s_clean) < 15:
            continue
        s_words = set(re.findall(r"[a-zA-Z0-9]+", s_clean.lower()))
        if q_words.intersection(s_words):
            relevant_sentences.append(s_clean)

    if relevant_sentences:
        answer_body = " ".join(relevant_sentences[:4])
        return {
            "answer": f"Based on the demonstration documentation: {answer_body}",
            "status": "answered"
        }
    elif content_lines:
        snippet = " ".join(content_lines[:3])
        return {
            "answer": f"Based on the demonstration documentation: {snippet}",
            "status": "answered"
        }
    else:
        return {
            "answer": f"I could not find relevant information answering '{question}' in the available demonstration knowledge base.",
            "status": "no_relevant_information"
        }


class ToolRegistry:
    """Tool invocation dispatcher ensuring consistent ToolResult packaging."""

    @staticmethod
    def execute(tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        try:
            if tool_name == "document_search":
                res = document_search(**arguments)
                return ToolResult(tool_name=tool_name, success=True, data=[r.model_dump() for r in res])
            elif tool_name == "document_lookup":
                res = document_lookup(**arguments)
                return ToolResult(tool_name=tool_name, success=(res is not None), data=res)
            elif tool_name == "document_metadata":
                res = document_metadata(**arguments)
                return ToolResult(tool_name=tool_name, success=(res is not None), data=res)
            elif tool_name == "final_response":
                res = final_response(**arguments)
                return ToolResult(tool_name=tool_name, success=True, data=res)
            else:
                return ToolResult(
                    tool_name=tool_name,
                    success=False,
                    data=None,
                    error_message=f"Unknown tool: '{tool_name}'"
                )
        except Exception as e:
            return ToolResult(tool_name=tool_name, success=False, data=None, error_message=str(e))
