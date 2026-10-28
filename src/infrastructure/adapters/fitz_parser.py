from pathlib import Path
from typing import List, Union
import uuid
import pymupdf

from src.domain.models import ChunkMetadata, DocumentChunk
from src.domain.ports.parser import DocumentParserPort


def split_text_into_chunks(
    text: str, 
    chunk_size: int = 1000, 
    chunk_overlap: int = 150
) -> List[str]:
    """Splits text into overlapping chunks, respecting paragraph and line breaks where possible."""
    cleaned_text = text.strip()
    if not cleaned_text:
        return []

    if len(cleaned_text) <= chunk_size:
        return [cleaned_text]

    chunks = []
    start = 0
    text_len = len(cleaned_text)

    while start < text_len:
        end = start + chunk_size
        if end >= text_len:
            chunk = cleaned_text[start:].strip()
            if chunk:
                chunks.append(chunk)
            break

        split_idx = cleaned_text.rfind("\n", start, end)
        if split_idx == -1 or split_idx < start + (chunk_size // 2):
            split_idx = cleaned_text.rfind(" ", start, end)

        if split_idx == -1 or split_idx <= start:
            split_idx = end

        chunk = cleaned_text[start:split_idx].strip()
        if chunk:
            chunks.append(chunk)

        start = max(start + 1, split_idx - chunk_overlap)

    return chunks


class FitzParserAdapter(DocumentParserPort):
    """Implementation of DocumentParserPort using PyMuPDF (fitz)."""

    def extract_chunks(
        self, 
        file_path: Union[str, Path], 
        chunk_size: int = 1000, 
        chunk_overlap: int = 150
    ) -> List[DocumentChunk]:
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"PDF file not found: {path}")

        doc = pymupdf.open(path)
        extracted_chunks: List[DocumentChunk] = []

        for page_idx, page in enumerate(doc):
            page_number = page_idx + 1
            page_text = page.get_text()
            if not page_text or not page_text.strip():
                continue

            page_chunks = split_text_into_chunks(
                page_text, 
                chunk_size=chunk_size, 
                chunk_overlap=chunk_overlap
            )

            for text_segment in page_chunks:
                metadata = ChunkMetadata(
                    source_document=path.name,
                    page_number=page_number,
                )
                extracted_chunks.append(
                    DocumentChunk(
                        id=str(uuid.uuid4()),
                        text=text_segment,
                        metadata=metadata,
                    )
                )

        doc.close()
        return extracted_chunks
