"""
Document ingestion, vector chunking, and local semantic retriever for Day 19.
"""

import os
import re
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer

from .config import WorkflowConfig

class LocalDocumentRetriever:
    """
    Local dense vector document retriever using SentenceTransformers and Cosine Similarity.
    Ingests synthetic policy documents, segments them into semantic chunks with metadata,
    and returns ranked chunks with normalized relevance scores.
    """
    _instance = None

    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = data_dir or WorkflowConfig.DATA_DIR
        self.model_name = WorkflowConfig.EMBEDDING_MODEL_NAME
        self.model = SentenceTransformer(self.model_name)
        self.chunks: List[Dict[str, Any]] = []
        self.chunk_embeddings: Optional[np.ndarray] = None
        self._simulate_error: bool = False
        
        # Load and index documents
        self.index_documents()

    @classmethod
    def get_instance(cls, data_dir: Optional[str] = None) -> "LocalDocumentRetriever":
        if cls._instance is None:
            cls._instance = cls(data_dir=data_dir)
        return cls._instance

    def set_simulate_error(self, simulate: bool) -> None:
        """Controlled error injection hook for testing failure recovery."""
        self._simulate_error = simulate

    def index_documents(self) -> int:
        """
        Scan data_dir, parse metadata headers, segment into chunks, and precompute embeddings.
        """
        self.chunks = []
        if not os.path.exists(self.data_dir):
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")

        for fname in sorted(os.listdir(self.data_dir)):
            if not fname.endswith(".txt"):
                continue
            fpath = os.path.join(self.data_dir, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract header metadata
            doc_id_match = re.search(r"^# Document ID:\s*(.+)$", content, re.MULTILINE)
            category_match = re.search(r"^# Category:\s*(.+)$", content, re.MULTILINE)
            source_match = re.search(r"^# Source:\s*(.+)$", content, re.MULTILINE)

            doc_id = doc_id_match.group(1).strip() if doc_id_match else f"DOC-{fname}"
            category = category_match.group(1).strip() if category_match else "General"
            source = source_match.group(1).strip() if source_match else "synthetic"

            # Split into sections by double newline or headers
            raw_sections = [s.strip() for s in content.split("\n\n") if s.strip()]
            
            chunk_seq = 1
            for section in raw_sections:
                # Skip pure header comment blocks
                if section.startswith("# Document ID:"):
                    continue
                # If section is very short (e.g. separator line), skip
                if set(section.strip()).issubset({"=", "-", " ", "\n"}):
                    continue
                if len(section) < 25:
                    continue

                chunk_id = f"{doc_id}-C{chunk_seq:02d}"
                self.chunks.append({
                    "chunk_id": chunk_id,
                    "document_id": doc_id,
                    "filename": fname,
                    "category": category,
                    "source": source,
                    "text": section
                })
                chunk_seq += 1

        # Precompute normalized embeddings
        texts = [c["text"] for c in self.chunks]
        if texts:
            # normalize_embeddings=True ensures cosine similarity == dot product
            self.chunk_embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        else:
            self.chunk_embeddings = np.empty((0, WorkflowConfig.EMBEDDING_DIMENSION), dtype=np.float32)

        return len(self.chunks)

    def retrieve(self, query: str, top_k: int = WorkflowConfig.DEFAULT_TOP_K) -> List[Dict[str, Any]]:
        """
        Execute semantic retrieval for a query.
        Returns top_k chunks sorted by cosine similarity in descending order.
        Scores are in range [0.0, 1.0] where 1.0 = identical semantic vector.
        """
        if self._simulate_error:
            raise RuntimeError("Simulated retriever connection failure: Vector database unreachable.")

        if not query or not query.strip():
            return []

        if not self.chunks or self.chunk_embeddings is None or len(self.chunk_embeddings) == 0:
            return []

        # Encode query to normalized vector
        query_vec = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True)[0]

        # Inner product of normalized vectors equals Cosine Similarity
        # Range of cosine similarity: [-1.0, 1.0], clip to [0.0, 1.0] for clarity
        similarities = np.dot(self.chunk_embeddings, query_vec)
        similarities = np.clip(similarities, 0.0, 1.0)

        # Sort descending
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            chunk_data = dict(self.chunks[idx])
            chunk_data["score"] = round(score, 4)
            results.append(chunk_data)

        return results
