from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Union
from src.domain.models import DocumentChunk


class DocumentParserPort(ABC):
    """Port for document parsing and chunking operations."""

    @abstractmethod
    def extract_chunks(
        self, 
        file_path: Union[str, Path], 
        chunk_size: int = 1000, 
        chunk_overlap: int = 150
    ) -> List[DocumentChunk]:
        """Extracts text chunks with exact page metadata from a PDF file."""
        pass
