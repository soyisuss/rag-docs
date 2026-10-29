from dataclasses import dataclass, field
from typing import Optional, List


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


@dataclass
class Citation:
    """Represents a citation source referencing a document and page."""
    document: str
    page: int
    score: float
    snippet: str


@dataclass
class AnswerResult:
    """Domain model representing the outcome of a RAG query execution."""
    query: str
    answer: str
    max_score: float
    threshold: float
    guardrail_passed: bool
    sources: List[Citation] = field(default_factory=list)
    message: Optional[str] = None


@dataclass
class DocumentItem:
    """Represents an indexed or available document in the system."""
    name: str
    pages: Optional[int] = None
    chunks_count: Optional[int] = None
