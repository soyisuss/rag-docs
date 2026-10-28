"""
Backward compatibility layer. Re-exports domain models.
"""
from src.domain.models import ChunkMetadata, DocumentChunk

__all__ = ["ChunkMetadata", "DocumentChunk"]
