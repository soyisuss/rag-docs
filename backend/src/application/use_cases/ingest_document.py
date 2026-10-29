import logging
from pathlib import Path
from typing import Union, List

from src.application.dtos import IngestResultDTO
from src.domain.ports.parser import DocumentParserPort
from src.domain.ports.embedder import EmbedderPort
from src.domain.ports.vector_store import VectorStorePort

logger = logging.getLogger(__name__)


class IngestDocumentUseCase:
    """
    Orchestrates ingestion of a document:
    1. Parse document into chunks with page numbers.
    2. Generate embeddings.
    3. Persist vectors in the vector store.
    """

    def __init__(
        self,
        parser: DocumentParserPort,
        embedder: EmbedderPort,
        vector_store: VectorStorePort,
    ):
        self.parser = parser
        self.embedder = embedder
        self.vector_store = vector_store

    def execute(self, file_path: Union[str, Path]) -> IngestResultDTO:
        path = Path(file_path)
        if not path.is_file():
            return IngestResultDTO(
                document_name=path.name,
                chunks_indexed=0,
                success=False,
                message=f"El archivo no existe: {path}",
            )

        logger.info(f"Extracting chunks from {path.name}...")
        chunks = self.parser.extract_chunks(path)
        if not chunks:
            return IngestResultDTO(
                document_name=path.name,
                chunks_indexed=0,
                success=True,
                message="El documento no contiene texto extraíble.",
            )

        # Generate embeddings
        texts = [c.text for c in chunks]
        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.embedder.generate_embeddings(texts)

        # Store in vector store
        logger.info(f"Storing chunks in vector store...")
        indexed_count = self.vector_store.upsert_chunks(chunks, embeddings)

        return IngestResultDTO(
            document_name=path.name,
            chunks_indexed=indexed_count,
            success=True,
            message=f"Se indexaron exitosamente {indexed_count} fragmentos.",
        )
