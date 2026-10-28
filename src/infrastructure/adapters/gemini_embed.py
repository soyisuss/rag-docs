import logging
from typing import List
from google import genai
from google.genai import types

from src.domain.ports.embedder import EmbedderPort
from src.infrastructure.config import (
    GEMINI_API_KEY, 
    GEMINI_EMBEDDING_MODEL, 
    VECTOR_DIMENSION
)

logger = logging.getLogger(__name__)


class GeminiEmbedderAdapter(EmbedderPort):
    """Generates dense vector embeddings using Google GenAI."""

    def __init__(
        self, 
        api_key: str = GEMINI_API_KEY, 
        model_name: str = GEMINI_EMBEDDING_MODEL, 
        dimension: int = VECTOR_DIMENSION
    ):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured in the environment.")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.config = types.EmbedContentConfig(output_dimensionality=dimension)

    def generate_embeddings(self, texts: List[str], batch_size: int = 50) -> List[List[float]]:
        if not texts:
            return []

        embeddings: List[List[float]] = []
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i : i + batch_size]
            response = self.client.models.embed_content(
                model=self.model_name,
                contents=batch_texts,
                config=self.config,
            )
            for emb in response.embeddings:
                embeddings.append(emb.values)

        return embeddings
