import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from qdrant_client import QdrantClient

from src.ingestion.indexer import (
    get_qdrant_client,
    generate_embeddings,
    DEFAULT_COLLECTION_NAME,
)

load_dotenv()

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

SIMILARITY_THRESHOLD = 0.70
TOP_K_RESULTS = 3


def search_semantic_documents(
    query: str,
    client: Optional[QdrantClient] = None,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    limit: int = TOP_K_RESULTS,
) -> List[Any]:
    """Executes semantic vector search on Qdrant."""
    if client is None:
        client = get_qdrant_client()

    if not client.collection_exists(collection_name=collection_name):
        logger.warning(f"Collection '{collection_name}' does not exist.")
        return []

    query_embeddings = generate_embeddings([query])
    if not query_embeddings:
        return []
    query_vector = query_embeddings[0]

    response = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=limit,
    )
    return response.points


def assemble_context(points: List[Any]) -> str:
    """Extracts text and metadata from Qdrant payloads and formats citations."""
    context_blocks = []
    for p in points:
        payload = p.payload or {}
        doc = payload.get("source_document", "Desconocido")
        page = payload.get("page_number", "N/A")
        text = payload.get("text", "").strip()
        context_blocks.append(f"[Archivo: {doc}, Página: {page}]\n{text}")

    return "\n\n".join(context_blocks)


def call_llm(prompt: str) -> str:
    """Sends prompt to Gemini Flash via Google GenAI SDK."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return (
            "[MODO DEMO / SIN CREDENCIALES LLM]\n"
            "El sistema recuperó los fragmentos pertinentes y aplicó los guardrails con éxito.\n"
            "Para generar la respuesta con Gemini, configura GEMINI_API_KEY en tu archivo .env."
        )

    from google import genai
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        contents=prompt,
    )
    return response.text


def query_rag_engine(
    query: str,
    threshold: float = SIMILARITY_THRESHOLD,
    limit: int = TOP_K_RESULTS,
    client: Optional[QdrantClient] = None,
) -> Dict[str, Any]:
    """
    Executes the full RAG inference pipeline:
    1. Semantic search in Qdrant.
    2. Guardrail evaluation (score threshold).
    3. Context assembly with citation constraints.
    4. LLM synthesis with Yael Bot persona.
    """
    points = search_semantic_documents(
        query=query, 
        client=client, 
        limit=limit,
    )

    max_score = max([p.score for p in points], default=0.0)

    # GUARDRAIL: Verify if evidence exceeds confidence threshold
    if not points or max_score < threshold:
        logger.info(f"Guardrail triggered: Max similarity score {max_score:.4f} is below threshold {threshold:.2f}")
        return {
            "query": query,
            "answer": "INSUFFICIENT_INFORMATION",
            "max_score": max_score,
            "threshold": threshold,
            "guardrail_passed": False,
            "sources": [],
            "message": (
                f"La consulta no superó el umbral mínimo de confianza ({threshold:.2f}). "
                "La ejecución del LLM fue abortada para prevenir alucinaciones y optimizar costes."
            ),
        }

    context_str = assemble_context(points)

    prompt = (
        "Actúa como Yael Bot, un asistente experto de consulta y análisis documental.\n"
        "Responde la consulta del usuario usando ÚNICAMENTE el contexto provisto a continuación.\n\n"
        "Reglas obligatorias:\n"
        "1. Basa cada afirmación estrictamente en el contexto.\n"
        "2. Al final de cada dato o respuesta, incluye la cita exacta en formato: [Archivo, Página].\n"
        "3. Si existen discrepancias o contradicciones en el contexto entre documentos o versiones, expón ambas posturas indicando la fuente de cada una.\n"
        "4. Si el contexto no contiene la respuesta completa, responde: 'INSUFFICIENT_INFORMATION'. No asumas información externa.\n\n"
        f"Contexto:\n{context_str}\n\n"
        f"Consulta del usuario:\n{query}\n\n"
        "Respuesta:"
    )

    answer_text = call_llm(prompt)

    sources = [
        {
            "document": p.payload.get("source_document"),
            "page": p.payload.get("page_number"),
            "score": round(p.score, 4),
            "snippet": (p.payload.get("text", "")[:200] + "...") if len(p.payload.get("text", "")) > 200 else p.payload.get("text", ""),
        }
        for p in points
    ]

    return {
        "query": query,
        "answer": answer_text,
        "max_score": round(max_score, 4),
        "threshold": threshold,
        "guardrail_passed": True,
        "sources": sources,
    }


if __name__ == "__main__":
    import sys

    user_query = sys.argv[1] if len(sys.argv) > 1 else "¿De qué trata este documento?"

    print(f"\n--- Probando RAG Engine (Yael Bot) ---")
    print(f"Consulta: '{user_query}'")

    result = query_rag_engine(user_query)
    print(f"\nGuardrail Superado: {result['guardrail_passed']} (Max Score: {result.get('max_score', 0):.4f})")
    print(f"\nRespuesta:\n{result['answer']}")

    if result.get("sources"):
        print("\nFuentes Recuperadas:")
        for s in result["sources"]:
            print(f"- [{s['document']}, Pág {s['page']}] (Score: {s['score']})")
