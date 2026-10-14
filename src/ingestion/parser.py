from pathlib import Path
from typing import List
import uuid
import pymupdf

from src.ingestion.models import ChunkMetadata, DocumentChunk


def split_text_into_chunks(
    text: str, 
    chunk_size: int = 1000, 
    chunk_overlap: int = 150
) -> List[str]:
    """
    Splits text into overlapping chunks, respecting paragraph and line breaks where possible.
    """
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


def extract_chunks_from_pdf(
    file_path: str | Path,
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> List[DocumentChunk]:
    """
    Parses a PDF file using PyMuPDF and produces DocumentChunks with exact page references.
    """
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


def parse_directory(directory_path: str | Path) -> List[DocumentChunk]:
    """
    Scans a directory for all .pdf files and extracts DocumentChunks from each.
    """
    dir_path = Path(directory_path)
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Directory not found: {dir_path}")

    all_chunks: List[DocumentChunk] = []
    pdf_files = sorted(dir_path.glob("*.pdf"))

    for pdf_file in pdf_files:
        chunks = extract_chunks_from_pdf(pdf_file)
        all_chunks.extend(chunks)

    return all_chunks


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "data/raw"
    target_path = Path(target)

    if target_path.is_file() and target_path.suffix.lower() == ".pdf":
        print(f"Parsing file: {target_path}")
        chunks = extract_chunks_from_pdf(target_path)
    elif target_path.is_dir():
        print(f"Parsing directory: {target_path}")
        chunks = parse_directory(target_path)
    else:
        print(f"Target '{target}' is not a valid file or directory.")
        sys.exit(0)

    print(f"Total chunks extracted: {len(chunks)}")
    for i, c in enumerate(chunks[:3]):
        print(f"\n--- Chunk {i+1} (Doc: {c.metadata.source_document}, Page: {c.metadata.page_number}) ---")
        print(c.text[:200] + ("..." if len(c.text) > 200 else ""))
