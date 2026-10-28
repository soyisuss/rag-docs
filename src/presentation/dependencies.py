from functools import lru_cache
from pathlib import Path

from src.infrastructure import config
from src.domain.ports.vector_store import VectorStorePort
from src.domain.ports.embedder import EmbedderPort
from src.domain.ports.llm import LLMPort
from src.domain.ports.parser import DocumentParserPort

from src.infrastructure.adapters.qdrant_store import QdrantStoreAdapter
from src.infrastructure.adapters.gemini_embed import GeminiEmbedderAdapter
from src.infrastructure.adapters.gemini_llm import GeminiLLMAdapter
from src.infrastructure.adapters.fitz_parser import FitzParserAdapter

from src.application.use_cases.ask_question import AskQuestionUseCase
from src.application.use_cases.ingest_document import IngestDocumentUseCase
from src.application.use_cases.delete_document import DeleteDocumentUseCase
from src.application.use_cases.list_documents import ListDocumentsUseCase


@lru_cache
def get_vector_store() -> VectorStorePort:
    return QdrantStoreAdapter(
        url=config.QDRANT_URL,
        api_key=config.QDRANT_API_KEY,
        collection_name=config.QDRANT_COLLECTION,
        dimension=config.VECTOR_DIMENSION,
    )


@lru_cache
def get_embedder() -> EmbedderPort:
    return GeminiEmbedderAdapter(
        api_key=config.GEMINI_API_KEY,
        model_name=config.GEMINI_EMBEDDING_MODEL,
        dimension=config.VECTOR_DIMENSION,
    )


@lru_cache
def get_llm() -> LLMPort:
    return GeminiLLMAdapter(
        api_key=config.GEMINI_API_KEY,
        model_name=config.GEMINI_MODEL,
    )


@lru_cache
def get_parser() -> DocumentParserPort:
    return FitzParserAdapter()


def get_data_dir() -> Path:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    return config.DATA_DIR


def get_ask_question_use_case() -> AskQuestionUseCase:
    return AskQuestionUseCase(
        vector_store=get_vector_store(),
        embedder=get_embedder(),
        llm=get_llm(),
        default_threshold=config.SIMILARITY_THRESHOLD,
        default_limit=config.TOP_K_RESULTS,
    )


def get_ingest_use_case() -> IngestDocumentUseCase:
    return IngestDocumentUseCase(
        parser=get_parser(),
        embedder=get_embedder(),
        vector_store=get_vector_store(),
    )


def get_delete_use_case() -> DeleteDocumentUseCase:
    return DeleteDocumentUseCase(
        vector_store=get_vector_store(),
        data_dir=get_data_dir(),
    )


def get_list_use_case() -> ListDocumentsUseCase:
    return ListDocumentsUseCase(
        vector_store=get_vector_store(),
        data_dir=get_data_dir(),
    )
