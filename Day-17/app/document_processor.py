"""
Day 17 — Document Processing & Chunking Engine
Extracts page-by-page text from PDFs and text files, performs character sliding-window
chunking, retains granular page and document metadata, and validates file integrity.
"""

import os
import io
import uuid
from typing import List, Dict, Any, Tuple
from pypdf import PdfReader
from pypdf.errors import PdfStreamError


# Default chunking configuration derived from Day 16 empirical findings
# (Best observed balance on the demonstration dataset; not claimed to be universally optimal)
DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 100
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB maximum upload limit


class DocumentProcessingError(Exception):
    """Custom exception for document parsing and validation failures."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


class DocumentProcessor:
    SUPPORTED_EXTENSIONS = {".pdf", ".txt"}

    @classmethod
    def validate_file(cls, filename: str, file_bytes: bytes) -> str:
        """
        Validate file extension, size, and non-empty content.
        Raises DocumentProcessingError with appropriate HTTP status code on failure.
        """
        if not filename or "." not in filename:
            raise DocumentProcessingError("Filename must contain a valid extension.", status_code=400)

        ext = os.path.splitext(filename)[1].lower()
        if ext not in cls.SUPPORTED_EXTENSIONS:
            supported = ", ".join(cls.SUPPORTED_EXTENSIONS)
            raise DocumentProcessingError(
                f"Unsupported file format '{ext}'. Supported formats are: {supported}",
                status_code=415
            )

        if len(file_bytes) == 0:
            raise DocumentProcessingError("Uploaded file is empty (0 bytes).", status_code=400)

        if len(file_bytes) > MAX_FILE_SIZE_BYTES:
            mb_size = len(file_bytes) / (1024 * 1024)
            raise DocumentProcessingError(
                f"File size ({mb_size:.2f} MB) exceeds maximum allowed limit of 10 MB.",
                status_code=413
            )

        return ext

    @classmethod
    def extract_text(cls, filename: str, file_bytes: bytes) -> Tuple[List[Dict[str, Any]], int]:
        """
        Extract text from file bytes page-by-page.
        Returns:
            List of pages: [{"page_number": int, "text": str}]
            Total character count
        """
        ext = cls.validate_file(filename, file_bytes)
        pages_data = []

        if ext == ".txt":
            try:
                text = file_bytes.decode("utf-8", errors="replace").strip()
            except Exception as e:
                raise DocumentProcessingError(f"Failed to decode text file: {str(e)}", status_code=400)

            if not text:
                raise DocumentProcessingError("Text file contains no readable text.", status_code=400)

            pages_data.append({"page_number": 1, "text": text})

        elif ext == ".pdf":
            try:
                stream = io.BytesIO(file_bytes)
                reader = PdfReader(stream)
            except Exception as e:
                raise DocumentProcessingError(f"Invalid or corrupted PDF file: {str(e)}", status_code=400)

            total_pages = len(reader.pages)
            if total_pages == 0:
                raise DocumentProcessingError("PDF contains zero pages.", status_code=400)

            extracted_any_text = False
            for page_idx, page in enumerate(reader.pages, start=1):
                try:
                    p_text = page.extract_text() or ""
                    p_text_clean = p_text.strip()
                    if p_text_clean:
                        extracted_any_text = True
                    pages_data.append({"page_number": page_idx, "text": p_text_clean})
                except Exception as e:
                    pages_data.append({"page_number": page_idx, "text": ""})

            if not extracted_any_text:
                raise DocumentProcessingError(
                    "PDF file contains no extractable text. Scanned images require OCR preprocessing.",
                    status_code=400
                )

        total_chars = sum(len(p["text"]) for p in pages_data)
        return pages_data, total_chars

    @classmethod
    def chunk_document(
        cls,
        document_id: str,
        filename: str,
        pages_data: List[Dict[str, Any]],
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_CHUNK_OVERLAP
    ) -> List[Dict[str, Any]]:
        """
        Split page-by-page text into character sliding-window chunks.
        Preserves page_number, document_id, filename, and offsets in chunk metadata.
        """
        chunks = []
        global_chunk_idx = 0
        step = chunk_size - overlap

        for p_info in pages_data:
            page_num = p_info["page_number"]
            text = p_info["text"]
            text_len = len(text)
            if not text_len:
                continue

            start = 0
            while start < text_len:
                end = min(start + chunk_size, text_len)
                chunk_str = text[start:end].strip()

                if len(chunk_str) >= 20:  # Avoid tiny fragments
                    chunk_id = f"{document_id}_p{page_num}_c{global_chunk_idx}"
                    chunks.append({
                        "id": chunk_id,
                        "text": chunk_str,
                        "metadata": {
                            "document_id": document_id,
                            "filename": filename,
                            "page_number": page_num,
                            "chunk_id": global_chunk_idx,
                            "chunk_size": len(chunk_str),
                            "char_start": start,
                            "char_end": end
                        }
                    })
                    global_chunk_idx += 1

                if end >= text_len:
                    break
                start += step

        return chunks
