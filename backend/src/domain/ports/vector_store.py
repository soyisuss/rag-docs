from abc import ABC, abstractmethod
from typing import List, Tuple, Any, Optional
from src.domain.models import DocumentChunk, Citation


class VectorStorePort(ABC):
    """Port for vector database operations (search, upsert, delete, list)."""

    @abstractmethod
    def search_similar(
        self, 
        vector: List[float], 
        limit: int = 3
    ) -> List[Tuple[DocumentChunk, float]]:
        """Searches for chunks most similar to the provided vector, returning chunks and similarity scores."""
        pass

    @abstractmethod
    def upsert_chunks(self, chunks: List[DocumentChunk], vectors: List[List[float]]) -> int:
        """Stores or updates chunks and their corresponding embeddings."""
        pass

    @abstractmethod
    def delete_by_document(self, document_name: str) -> None:
        """Purges all vectors and points related to a specific document."""
        pass

    @abstractmethod
    def list_indexed_document_names(self, limit: int = 500) -> List[str]:
        """Lists the distinct document names stored in the vector collection."""
        pass
