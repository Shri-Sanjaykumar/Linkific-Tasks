"""
Day 17 — RAG Service Orchestrator
Integrates ChromaDB vector store, EmbeddingService, and T5 Seq2Seq generator.
Manages document ingestion, semantic search with source attribution, and document deletion.
"""

import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from .embeddings import EmbeddingService
from .document_processor import DocumentProcessor, DocumentProcessingError, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP


class RAGService:
    _instance = None

    def __init__(self):
        print("Initializing RAG Service...")
        self.embedding_service = EmbeddingService.get_instance()

        # Initialize local T5-small generator (from Day 16)
        self.gen_model_name = "t5-small"
        print(f"Loading Generator Model: {self.gen_model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.gen_model_name)
        self.generator = AutoModelForSeq2SeqLM.from_pretrained(self.gen_model_name)
        print("Generator Model initialized successfully.")

        # In-memory ChromaDB client
        self.chroma_client = chromadb.Client()
        self.collection_name = "day17_rag_documents"
        try:
            self.chroma_client.delete_collection(self.collection_name)
        except Exception:
            pass
        self.collection = self.chroma_client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        # Document registry tracking uploaded files
        # key: document_id -> value: DocumentInfo dict
        self.documents_registry: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def process_and_index_document(
        self,
        filename: str,
        file_bytes: bytes,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_CHUNK_OVERLAP
    ) -> Dict[str, Any]:
        """
        Validate, extract, chunk, embed, and store a document in ChromaDB.
        """
        document_id = str(uuid.uuid4())[:8]

        # 1. Extract text
        pages_data, total_chars = DocumentProcessor.extract_text(filename, file_bytes)

        # 2. Chunk text
        chunks = DocumentProcessor.chunk_document(
            document_id=document_id,
            filename=filename,
            pages_data=pages_data,
            chunk_size=chunk_size,
            overlap=overlap
        )

        if not chunks:
            raise DocumentProcessingError(
                "Document could not be partitioned into valid chunks.",
                status_code=400
            )

        # 3. Generate embeddings
        chunk_texts = [c["text"] for c in chunks]
        embeddings = self.embedding_service.encode_texts(chunk_texts)

        # 4. Store in ChromaDB
        ids = [c["id"] for c in chunks]
        metas = [c["metadata"] for c in chunks]

        self.collection.add(
            ids=ids,
            documents=chunk_texts,
            embeddings=embeddings.tolist(),
            metadatas=metas
        )

        # 5. Register document
        doc_record = {
            "document_id": document_id,
            "filename": filename,
            "file_type": os.path.splitext(filename)[1].lower(),
            "file_size_bytes": len(file_bytes),
            "pages_count": len(pages_data),
            "chunks_count": len(chunks),
            "upload_timestamp": datetime.now().isoformat()
        }
        self.documents_registry[document_id] = doc_record

        return {
            "document_id": document_id,
            "filename": filename,
            "file_type": doc_record["file_type"],
            "file_size_bytes": doc_record["file_size_bytes"],
            "pages_count": doc_record["pages_count"],
            "chunks_count": doc_record["chunks_count"],
            "chunk_size": chunk_size,
            "overlap": overlap,
            "message": f"Document '{filename}' successfully processed and indexed ({len(chunks)} chunks created)."
        }

    def list_documents(self) -> List[Dict[str, Any]]:
        """Return all currently indexed documents."""
        return list(self.documents_registry.values())

    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """
        Delete all chunks for a document from ChromaDB and remove from registry.
        """
        if document_id not in self.documents_registry:
            raise DocumentProcessingError(
                f"Document with ID '{document_id}' not found.",
                status_code=404
            )

        doc_record = self.documents_registry[document_id]
        filename = doc_record["filename"]
        chunks_count = doc_record["chunks_count"]

        # Delete from ChromaDB by metadata filter
        self.collection.delete(where={"document_id": document_id})
        del self.documents_registry[document_id]

        return {
            "document_id": document_id,
            "filename": filename,
            "chunks_removed": chunks_count,
            "message": f"Document '{filename}' and {chunks_count} indexed chunks were successfully removed."
        }

    def ask_question(self, question: str, top_k: int = 2) -> Dict[str, Any]:
        """
        Semantic search + local T5 Seq2Seq generation.
        """
        if not self.documents_registry:
            raise DocumentProcessingError(
                "No documents have been uploaded yet. Please upload a document before asking questions.",
                status_code=400
            )

        clean_q = question.strip()
        if not clean_q or len(clean_q) < 3:
            raise DocumentProcessingError(
                "Question must contain at least 3 non-whitespace characters.",
                status_code=400
            )

        # 1. Encode query
        q_emb = self.embedding_service.encode_query(clean_q)

        # 2. Query ChromaDB
        results = self.collection.query(
            query_embeddings=[q_emb],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        retrieved_docs = results["documents"][0] if results["documents"] else []
        retrieved_metas = results["metadatas"][0] if results["metadatas"] else []
        retrieved_dists = results["distances"][0] if results["distances"] else []

        if not retrieved_docs:
            return {
                "question": clean_q,
                "answer": "No relevant context found in the uploaded documents.",
                "total_sources": 0,
                "sources": []
            }

        # 3. Assemble context and generate answer with T5
        context_str = " ".join(retrieved_docs)
        prompt = f"question: {clean_q} context: {context_str}"

        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
        outputs = self.generator.generate(
            **inputs,
            max_new_tokens=60,
            num_beams=2,
            early_stopping=True
        )
        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

        if not answer or len(answer) < 3:
            answer = "Information not specified in the provided documentation."

        # 4. Format sources with cosine similarity (similarity = 1.0 - distance)
        sources = []
        for doc_text, meta, dist in zip(retrieved_docs, retrieved_metas, retrieved_dists):
            cos_dist = round(float(dist), 4)
            sim_score = round(max(0.0, 1.0 - cos_dist), 4)
            sources.append({
                "document_id": meta["document_id"],
                "filename": meta["filename"],
                "page_number": int(meta["page_number"]),
                "chunk_id": int(meta["chunk_id"]),
                "similarity_score": sim_score,
                "cosine_distance": cos_dist,
                "text_snippet": doc_text[:140] + ("..." if len(doc_text) > 140 else "")
            })

        return {
            "question": clean_q,
            "answer": answer,
            "total_sources": len(sources),
            "sources": sources
        }

    def get_health_stats(self) -> Dict[str, Any]:
        """Return live health and index statistics."""
        return {
            "status": "healthy",
            "application": "Linkific RAG API",
            "version": "1.0.0",
            "documents_indexed": len(self.documents_registry),
            "total_chunks": self.collection.count(),
            "embedding_model": self.embedding_service.model_name,
            "generator_model": self.gen_model_name
        }
