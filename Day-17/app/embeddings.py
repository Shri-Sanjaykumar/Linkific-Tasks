"""
Day 17 — Embeddings Service
Reuses the Day 16 all-MiniLM-L6-v2 embedding model generating 384-dimensional dense vectors.
"""

from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    _instance = None

    def __init__(self):
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        print(f"Loading Embedding Model: {self.model_name}...")
        self.model = SentenceTransformer(self.model_name)
        if hasattr(self.model, "get_embedding_dimension"):
            self.dimension = self.model.get_embedding_dimension()
        else:
            self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"Embedding Model initialized. Vector dimensionality: {self.dimension}")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """
        Encode a list of text strings into normalized 384-dimensional dense vectors.
        Normalization ensures Inner Product equals Cosine Similarity.
        """
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)
        return self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)

    def encode_query(self, query: str) -> List[float]:
        """
        Encode a single query string into a normalized embedding list for ChromaDB.
        """
        emb = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        return emb[0].tolist()
