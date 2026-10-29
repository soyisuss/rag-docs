from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CitationDTO:
    document: str
    page: int
    score: float
    snippet: str


@dataclass
class ChatRequestDTO:
    query: str
    similarity_threshold: Optional[float] = None
    limit: Optional[int] = None


@dataclass
class ChatResponseDTO:
    query: str
    answer: str
    max_score: float
    threshold: float
    guardrail_passed: bool
    sources: List[CitationDTO] = field(default_factory=list)
    message: Optional[str] = None


@dataclass
class DocumentItemDTO:
    name: str
    in_storage: bool = True
    in_vector_store: bool = True


@dataclass
class IngestResultDTO:
    document_name: str
    chunks_indexed: int
    success: bool
    message: Optional[str] = None
