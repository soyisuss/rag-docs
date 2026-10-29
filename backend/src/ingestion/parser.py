"""
Backward compatibility layer. Re-exports parser utilities and CLI.
"""
from pathlib import Path
from typing import List, Union

from src.domain.models import DocumentChunk
from src.infrastructure.adapters.fitz_parser import (
    FitzParserAdapter, 
    split_text_into_chunks,
)

_adapter = FitzParserAdapter()


def extract_chunks_from_pdf(
    file_path: Union[str, Path],
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> List[DocumentChunk]:
    return _adapter.extract_chunks(file_path, chunk_size, chunk_overlap)


def parse_directory(directory_path: Union[str, Path]) -> List[DocumentChunk]:
    dir_path = Path(directory_path)
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Directory not found: {dir_path}")

    all_chunks: List[DocumentChunk] = []
    pdf_files = sorted(dir_path.glob("*.pdf"))
    for pdf in pdf_files:
        all_chunks.extend(extract_chunks_from_pdf(pdf))
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
