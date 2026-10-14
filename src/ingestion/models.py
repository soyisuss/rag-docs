from dataclasses import dataclass
from typing import Optional


@dataclass
class ChunkMetadata:
    """Metadata schema for ingested document chunks, tracking source and page."""
    source_document: str
    page_number: int


@dataclass
class DocumentChunk:
    """Unified representation of an extracted chunk with text and metadata."""
    text: str
    metadata: ChunkMetadata
    id: Optional[str] = None
