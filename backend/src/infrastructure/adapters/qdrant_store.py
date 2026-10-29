import logging
from typing import List, Tuple, Optional
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, 
    VectorParams, 
    PointStruct, 
    Filter, 
    FieldCondition, 
    MatchValue,
    PayloadSchemaType
)

from src.domain.models import DocumentChunk, ChunkMetadata
from src.domain.ports.vector_store import VectorStorePort
from src.infrastructure.config import (
    QDRANT_URL, 
    QDRANT_API_KEY, 
    QDRANT_COLLECTION, 
    VECTOR_DIMENSION
)

logger = logging.getLogger(__name__)


class QdrantStoreAdapter(VectorStorePort):
    """Implementation of VectorStorePort using Qdrant (Cloud or local)."""

    def __init__(
        self,
        url: str = QDRANT_URL,
        api_key: Optional[str] = QDRANT_API_KEY,
        collection_name: str = QDRANT_COLLECTION,
        dimension: int = VECTOR_DIMENSION,
    ):
        if not url:
            raise ValueError("QDRANT_URL is not configured in the environment.")
        self.url = url
        self.api_key = api_key
        self.collection_name = collection_name
        self.dimension = dimension
        self.client = QdrantClient(url=url, api_key=api_key)
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Ensures collection exists with appropriate index."""
        if not self.client.collection_exists(collection_name=self.collection_name):
            logger.info(f"Creating Qdrant collection '{self.collection_name}'...")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.dimension, distance=Distance.COSINE),
            )
        try:
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="source_document",
                field_schema=PayloadSchemaType.KEYWORD,
            )
        except Exception as e:
            logger.debug(f"Payload index check: {e}")

    def search_similar(
        self, 
        vector: List[float], 
        limit: int = 5
    ) -> List[Tuple[DocumentChunk, float]]:
        if not self.client.collection_exists(collection_name=self.collection_name):
            return []

        # Solicitamos un margen más amplio para filtrar duplicados
        fetch_limit = max(limit * 3, 15)
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=vector,
            limit=fetch_limit,
        )

        results: List[Tuple[DocumentChunk, float]] = []
        seen_signatures = set()

        for point in response.points:
            payload = point.payload or {}
            raw_text = (payload.get("text") or "").strip()
            doc_name = payload.get("source_document", "Desconocido")
            page_num = payload.get("page_number", 0)

            # Firma para deduplicación: documento, página y primeros 50 caracteres normalizados
            normalized_snippet = " ".join(raw_text.split()[:15])
            signature = (doc_name, page_num, normalized_snippet)

            if signature in seen_signatures:
                continue
            seen_signatures.add(signature)

            chunk = DocumentChunk(
                id=str(point.id),
                text=raw_text,
                metadata=ChunkMetadata(
                    source_document=doc_name,
                    page_number=page_num,
                )
            )
            results.append((chunk, float(point.score)))
            if len(results) >= limit:
                break

        return results

    def upsert_chunks(self, chunks: List[DocumentChunk], vectors: List[List[float]]) -> int:
        if not chunks or not vectors or len(chunks) != len(vectors):
            return 0

        self._ensure_collection()

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

        self.client.upsert(collection_name=self.collection_name, points=points)
        return len(points)

    def delete_by_document(self, document_name: str) -> None:
        if not self.client.collection_exists(collection_name=self.collection_name):
            return

        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="source_document",
                        match=MatchValue(value=document_name),
                    )
                ]
            ),
        )

    def list_indexed_document_names(self, limit: int = 500) -> List[str]:
        if not self.client.collection_exists(collection_name=self.collection_name):
            return []

        points, _ = self.client.scroll(
            collection_name=self.collection_name,
            limit=limit,
            with_payload=["source_document"],
            with_vectors=False,
        )
        names = set()
        for p in points:
            if p.payload and "source_document" in p.payload:
                names.add(p.payload["source_document"])

        return sorted(list(names))
