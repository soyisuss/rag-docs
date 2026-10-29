"""
Backward compatibility layer. Re-exports indexing functions and CLI.
"""
import sys
from pathlib import Path
from typing import List, Optional

from qdrant_client import QdrantClient

from src.domain.models import DocumentChunk
from src.infrastructure.adapters.fitz_parser import FitzParserAdapter
from src.infrastructure.adapters.gemini_embed import GeminiEmbedderAdapter
from src.infrastructure.adapters.qdrant_store import QdrantStoreAdapter
from src.infrastructure import config
from src.ingestion.parser import parse_directory

DEFAULT_COLLECTION_NAME = config.QDRANT_COLLECTION
VECTOR_DIMENSION = config.VECTOR_DIMENSION


def get_qdrant_client() -> QdrantClient:
    adapter = QdrantStoreAdapter(
        url=config.QDRANT_URL,
        api_key=config.QDRANT_API_KEY,
        collection_name=config.QDRANT_COLLECTION,
        dimension=config.VECTOR_DIMENSION,
    )
    return adapter.client


def init_collection(
    client: QdrantClient, 
    collection_name: str = DEFAULT_COLLECTION_NAME, 
    vector_size: int = VECTOR_DIMENSION
) -> None:
    QdrantStoreAdapter(
        url=config.QDRANT_URL,
        api_key=config.QDRANT_API_KEY,
        collection_name=collection_name,
        dimension=vector_size,
    )


def delete_document_from_qdrant(
    doc_name: str,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    client: Optional[QdrantClient] = None,
) -> None:
    adapter = QdrantStoreAdapter(
        url=config.QDRANT_URL,
        api_key=config.QDRANT_API_KEY,
        collection_name=collection_name,
        dimension=config.VECTOR_DIMENSION,
    )
    adapter.delete_by_document(doc_name)


def generate_embeddings(texts: List[str], batch_size: int = 50) -> List[List[float]]:
    adapter = GeminiEmbedderAdapter()
    return adapter.generate_embeddings(texts, batch_size=batch_size)


def index_documents(
    chunks: List[DocumentChunk],
    collection_name: str = DEFAULT_COLLECTION_NAME,
    client: Optional[QdrantClient] = None,
) -> int:
    embedder = GeminiEmbedderAdapter()
    store = QdrantStoreAdapter(
        url=config.QDRANT_URL,
        api_key=config.QDRANT_API_KEY,
        collection_name=collection_name,
        dimension=config.VECTOR_DIMENSION,
    )
    vectors = embedder.generate_embeddings([c.text for c in chunks])
    return store.upsert_chunks(chunks, vectors)


if __name__ == "__main__":
    raw_dir = Path("data/raw")
    if not raw_dir.is_dir() or not list(raw_dir.glob("*.pdf")):
        print(f"No se encontraron documentos PDF en {raw_dir}.")
        sys.exit(0)

    print(f"Procesando documentos desde: {raw_dir}")
    chunks = parse_directory(raw_dir)
    indexed_count = index_documents(chunks)
    print(f"Resultado: {indexed_count} fragmentos indexados exitosamente en Qdrant.")
