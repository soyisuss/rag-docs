import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import logging
from typing import List, Optional
import uuid
from dotenv import load_dotenv

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from src.ingestion.models import DocumentChunk
from src.ingestion.parser import parse_directory

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "documents")
VECTOR_DIMENSION = 768


def get_qdrant_client() -> QdrantClient:
    """
    Initializes and returns the remote Qdrant client based on environment variables.
    Requires QDRANT_URL to connect to the remote Qdrant service.
    """
    qdrant_url = os.getenv("QDRANT_URL", "").strip()
    qdrant_api_key = os.getenv("QDRANT_API_KEY", "").strip() or None

    if not qdrant_url:
        raise ValueError(
            "QDRANT_URL no está configurada. Define la URL del servicio remoto de Qdrant en el archivo .env."
        )

    logger.info(f"Connecting to remote Qdrant at: {qdrant_url}")
    return QdrantClient(url=qdrant_url, api_key=qdrant_api_key)


def init_collection(
    client: QdrantClient, 
    collection_name: str = DEFAULT_COLLECTION_NAME, 
    vector_size: int = VECTOR_DIMENSION
) -> None:
    """Ensures that the target Qdrant collection exists."""
    if not client.collection_exists(collection_name=collection_name):
        logger.info(f"Creating collection '{collection_name}' with vector size {vector_size} (Cosine distance)...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
    else:
        logger.info(f"Collection '{collection_name}' already exists.")

    try:
        from qdrant_client.models import PayloadSchemaType
        client.create_payload_index(
            collection_name=collection_name,
            field_name="source_document",
            field_schema=PayloadSchemaType.KEYWORD,
        )
    except Exception as e:
        logger.debug(f"Payload index creation info: {e}")


def delete_document_from_qdrant(
    doc_name: str,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    client: Optional[QdrantClient] = None,
) -> None:
    """Removes all vectors belonging to the specified document from Qdrant."""
    if client is None:
        client = get_qdrant_client()

    if not client.collection_exists(collection_name=collection_name):
        return

    from qdrant_client.models import Filter, FieldCondition, MatchValue
    client.delete(
        collection_name=collection_name,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="source_document",
                    match=MatchValue(value=doc_name),
                )
            ]
        ),
    )
    logger.info(f"Deleted document '{doc_name}' from Qdrant collection '{collection_name}'.")


def generate_embeddings(
    texts: List[str], 
    batch_size: int = 50
) -> List[List[float]]:
    """Generates 768-dimensional embeddings using Google GenAI."""
    if not texts:
        return []

    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not gemini_key:
        raise ValueError("GEMINI_API_KEY no está configurada en las variables de entorno.")

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=gemini_key)
    config = types.EmbedContentConfig(output_dimensionality=VECTOR_DIMENSION)
    embeddings: List[List[float]] = []

    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i : i + batch_size]
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=batch_texts,
            config=config,
        )
        for emb in response.embeddings:
            embeddings.append(emb.values)

    return embeddings


def index_documents(
    chunks: List[DocumentChunk],
    collection_name: str = DEFAULT_COLLECTION_NAME,
    client: Optional[QdrantClient] = None,
) -> int:
    """Generates embeddings for chunks and upserts them into Qdrant."""
    if not chunks:
        logger.warning("No chunks to index.")
        return 0

    if client is None:
        client = get_qdrant_client()

    init_collection(client, collection_name=collection_name, vector_size=VECTOR_DIMENSION)

    texts = [c.text for c in chunks]
    logger.info(f"Generating embeddings for {len(texts)} chunks...")
    vectors = generate_embeddings(texts)

    points = [
        PointStruct(
            id=chunk.id or str(uuid.uuid4()),
            vector=vector,
            payload={
                "text": chunk.text,
                "source_document": chunk.metadata.source_document,
                "page_number": chunk.metadata.page_number,
            },
        )
        for chunk, vector in zip(chunks, vectors)
    ]

    logger.info(f"Upserting {len(points)} points into Qdrant collection '{collection_name}'...")
    client.upsert(collection_name=collection_name, points=points)
    logger.info("Indexing completed successfully.")
    return len(points)


if __name__ == "__main__":
    raw_dir = Path("data/raw")
    if not raw_dir.is_dir() or not list(raw_dir.glob("*.pdf")):
        logger.warning(f"No se encontraron documentos PDF en {raw_dir}.")
        sys.exit(0)

    logger.info(f"Procesando documentos desde: {raw_dir}")
    chunks = parse_directory(raw_dir)
    indexed_count = index_documents(chunks)
    print(f"Resultado: {indexed_count} fragmentos indexados exitosamente en Qdrant.")
