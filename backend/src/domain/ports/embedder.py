from abc import ABC, abstractmethod
from typing import List


class EmbedderPort(ABC):
    """Port for generating dense vector representations of text."""

    @abstractmethod
    def generate_embeddings(self, texts: List[str], batch_size: int = 50) -> List[List[float]]:
        """Generates embeddings for a batch of text strings."""
        pass
