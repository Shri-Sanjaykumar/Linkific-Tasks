"""
Day 22 — Research Agent Implementation
Responsibilities:
- Ingests enterprise document corpus from approved data sources.
- Performs semantic/lexical evidence retrieval based on user query and revision directives.
- Preserves full provenance metadata (doc ID, title, author, version, relevance score).
- Formats and submits structured ResearchFindings into the Centralized Shared State.
"""

import os
import json
import re
import logging
from typing import List, Dict, Any, Optional
from .base import BaseAgent
from ..schemas import (
    AgentRole,
    MessageType,
    EvidenceItem,
    ResearchFindings
)
from ..config import config

logger = logging.getLogger("LinkificMultiAgent.ResearchAgent")


class ResearchAgent(BaseAgent):
    """
    Dedicated Research Agent for enterprise document intelligence.
    Extracts grounded facts from company policies and reports missing information.
    """

    def __init__(self, state_manager, bus, corpus_path: Optional[str] = None):
        super().__init__(AgentRole.RESEARCH, state_manager, bus)
        self.corpus_path = corpus_path or config.CORPUS_FILE
        self._corpus: List[Dict[str, Any]] = self._load_corpus()

    def _load_corpus(self) -> List[Dict[str, Any]]:
        """Loads vetted documents from the enterprise corpus file."""
        if not os.path.exists(self.corpus_path):
            logger.warning(f"Corpus file not found at {self.corpus_path}. Initializing empty corpus.")
            return []
        try:
            with open(self.corpus_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading corpus from {self.corpus_path}: {e}")
            return []

    def execute(self, task_id: str, context: Optional[Dict[str, Any]] = None) -> ResearchFindings:
        """
        Executes evidence retrieval for the workflow query.
        Handles both initial broad searches and focused revision re-queries.
        """
        self.state_manager.update_agent_status(self.role, self.role, "running")
        snapshot = self.state_manager.get_snapshot()
        query = snapshot.user_query
        
        # Check if executing in revision mode with targeted keywords
        is_revision = False
        target_focus = []
        if context and context.get("is_revision"):
            is_revision = True
            target_focus = context.get("target_focus", [])
            query = f"{query} {' '.join(target_focus)}"
            logger.info(f"ResearchAgent executing revision search with expanded query: '{query}'")

        top_k = config.RESEARCH_REVISE_TOP_K if is_revision else config.RESEARCH_TOP_K

        # Retrieve matching evidence items
        evidence_items, unresolved = self._search_corpus(query, top_k)

        status_label = "complete" if evidence_items else "no_results"
        if unresolved and evidence_items:
            status_label = "partial"

        findings = ResearchFindings(
            query=query,
            evidence=evidence_items,
            unresolved_queries=unresolved,
            search_parameters={"top_k": top_k, "is_revision": is_revision, "corpus_size": len(self._corpus)},
            status=status_label
        )

        # Update Shared State
        self.state_manager.set_research_findings(self.role, findings)
        self.state_manager.update_agent_status(self.role, self.role, "completed")

        # Notify Analyzer via Message Bus
        self.send_output(
            task_id=task_id,
            receiver=AgentRole.ANALYZER,
            message_type=MessageType.RESEARCH_SUBMISSION,
            payload={"status": status_label, "evidence_count": len(evidence_items)},
            evidence_ids=[e.source_id for e in evidence_items]
        )

        return findings

    def _search_corpus(self, query: str, top_k: int) -> tuple[List[EvidenceItem], List[str]]:
        """Scoring algorithm evaluating term frequency and token overlap across corpus documents."""
        if not self._corpus:
            return [], [query]

        tokens = set(re.findall(r"\b\w{3,}\b", query.lower()))
        # Remove common stop words
        stopwords = {"what", "when", "where", "which", "with", "from", "that", "this", "have", "been", "will", "your", "does"}
        filtered_tokens = tokens - stopwords

        if not filtered_tokens:
            filtered_tokens = tokens

        scored_docs = []
        for doc in self._corpus:
            text = (doc.get("title", "") + " " + doc.get("content", "") + " " + doc.get("category", "")).lower()
            doc_tokens = set(re.findall(r"\b\w{3,}\b", text))
            
            # Intersection score
            overlap = filtered_tokens.intersection(doc_tokens)
            score = len(overlap) / max(len(filtered_tokens), 1)

            # Boost exact phrases or category match
            for t in filtered_tokens:
                if t in doc.get("category", "").lower():
                    score += 0.15

            if score > config.SIMILARITY_THRESHOLD:
                scored_docs.append((min(round(score, 4), 1.0), doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        selected = scored_docs[:top_k]

        evidence_items = []
        for score, doc in selected:
            evidence_items.append(EvidenceItem(
                source_id=doc.get("id", "DOC-UNKNOWN"),
                title=doc.get("title", "Untitled Document"),
                category=doc.get("category", "General"),
                excerpt=doc.get("content", ""),
                relevance_score=score,
                version=doc.get("version", "1.0"),
                author=doc.get("author", "Enterprise Operations")
            ))

        unresolved = []
        if not evidence_items:
            unresolved.append(f"No enterprise documentation matching query concepts: {list(filtered_tokens)}")

        return evidence_items, unresolved
