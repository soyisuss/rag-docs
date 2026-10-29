"""
Backward compatibility layer. Re-exports retrieval functions and CLI.
"""
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient

from src.application.dtos import ChatRequestDTO
from src.application.use_cases.ask_question import AskQuestionUseCase
from src.presentation.dependencies import (
    get_ask_question_use_case,
    get_vector_store,
    get_embedder,
    get_llm,
)
from src.infrastructure import config

SIMILARITY_THRESHOLD = config.SIMILARITY_THRESHOLD
TOP_K_RESULTS = config.TOP_K_RESULTS


def query_rag_engine(
    query: str,
    threshold: float = SIMILARITY_THRESHOLD,
    limit: int = TOP_K_RESULTS,
    client: Optional[QdrantClient] = None,
) -> Dict[str, Any]:
    use_case = AskQuestionUseCase(
        vector_store=get_vector_store(),
        embedder=get_embedder(),
        llm=get_llm(),
        default_threshold=threshold,
        default_limit=limit,
    )
    result = use_case.execute(
        ChatRequestDTO(
            query=query,
            similarity_threshold=threshold,
            limit=limit,
        )
    )

    return {
        "query": result.query,
        "answer": result.answer,
        "max_score": result.max_score,
        "threshold": result.threshold,
        "guardrail_passed": result.guardrail_passed,
        "sources": [
            {
                "document": s.document,
                "page": s.page,
                "score": s.score,
                "snippet": s.snippet,
            }
            for s in result.sources
        ],
        "message": result.message,
    }


if __name__ == "__main__":
    import sys

    user_query = sys.argv[1] if len(sys.argv) > 1 else "¿De qué trata este documento?"

    print(f"\n--- Probando RAG Engine (Yael Bot) ---")
    print(f"Consulta: '{user_query}'")

    res = query_rag_engine(user_query)
    print(f"\nGuardrail Superado: {res['guardrail_passed']} (Max Score: {res.get('max_score', 0):.4f})")
    print(f"\nRespuesta:\n{res['answer']}")

    if res.get("sources"):
        print("\nFuentes Recuperadas:")
        for s in res["sources"]:
            print(f"- [{s['document']}, Pág {s['page']}] (Score: {s['score']})")
