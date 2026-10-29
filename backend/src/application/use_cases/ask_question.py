import logging
from typing import Optional

from src.application.dtos import ChatRequestDTO, ChatResponseDTO, CitationDTO
from src.domain.ports.vector_store import VectorStorePort
from src.domain.ports.embedder import EmbedderPort
from src.domain.ports.llm import LLMPort

logger = logging.getLogger(__name__)

DEFAULT_SIMILARITY_THRESHOLD = 0.70
DEFAULT_TOP_K = 5


class AskQuestionUseCase:
    """
    Orchestrates the RAG question-answering workflow:
    1. Embed query
    2. Retrieve similar chunks
    3. Evaluate Confidence Guardrail
    4. Assemble context & prompt
    5. Generate grounded response with citations
    """

    def __init__(
        self,
        vector_store: VectorStorePort,
        embedder: EmbedderPort,
        llm: LLMPort,
        default_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
        default_limit: int = DEFAULT_TOP_K,
    ):
        self.vector_store = vector_store
        self.embedder = embedder
        self.llm = llm
        self.default_threshold = default_threshold
        self.default_limit = default_limit

    def execute(self, request: ChatRequestDTO) -> ChatResponseDTO:
        threshold = request.similarity_threshold or self.default_threshold
        limit = request.limit or self.default_limit

        query = request.query.strip()
        if not query:
            return ChatResponseDTO(
                query="",
                answer="Por favor, ingresa una consulta válida.",
                max_score=0.0,
                threshold=threshold,
                guardrail_passed=False,
                sources=[],
                message="Consulta vacía.",
            )

        # 1. Embed query
        query_embeddings = self.embedder.generate_embeddings([query])
        if not query_embeddings:
            return ChatResponseDTO(
                query=query,
                answer="INSUFFICIENT_INFORMATION",
                max_score=0.0,
                threshold=threshold,
                guardrail_passed=False,
                sources=[],
                message="No se pudo generar el vector de búsqueda para la consulta.",
            )

        query_vector = query_embeddings[0]

        # 2. Vector search
        matched_chunks = self.vector_store.search_similar(vector=query_vector, limit=limit)
        max_score = max([score for _, score in matched_chunks], default=0.0)

        # 3. Guardrail evaluation
        if not matched_chunks or max_score < threshold:
            logger.info(
                f"Confidence guardrail triggered: max score {max_score:.4f} < threshold {threshold:.2f}"
            )
            return ChatResponseDTO(
                query=query,
                answer="INSUFFICIENT_INFORMATION",
                max_score=round(max_score, 4),
                threshold=threshold,
                guardrail_passed=False,
                sources=[],
                message=(
                    f"La consulta no superó el umbral mínimo de confianza ({threshold:.2f}). "
                    "La llamada al LLM fue abortada para prevenir alucinaciones."
                ),
            )

        # 4. Context assembly
        context_blocks = []
        citations = []
        for chunk, score in matched_chunks:
            doc = chunk.metadata.source_document
            page = chunk.metadata.page_number
            text = chunk.text.strip()
            context_blocks.append(f"[Archivo: {doc}, Página: {page}]\n{text}")

            snippet = (text[:200] + "...") if len(text) > 200 else text
            citations.append(
                CitationDTO(
                    document=doc,
                    page=page,
                    score=round(score, 4),
                    snippet=snippet,
                )
            )

        context_str = "\n\n".join(context_blocks)

        prompt = (
            "Actúa como Yael Bot, un asistente experto de consulta y análisis documental.\n"
            "Responde la consulta del usuario usando ÚNICAMENTE el contexto provisto a continuación.\n\n"
            "Reglas obligatorias:\n"
            "1. Basa cada afirmación estrictamente en el contexto.\n"
            "2. Al final de cada dato o respuesta, incluye la cita exacta en formato: [Archivo, Página].\n"
            "3. Si existen discrepancias o contradicciones en el contexto entre documentos o versiones, expón ambas posturas indicando la fuente de cada una.\n"
            "4. Si el contexto contiene información parcial, responde lo que se encuentre explícito citando la fuente y aclara con precisión qué detalle adicional no aparece. Solo si el contexto no contiene información relevante para la consulta, responde: 'INSUFFICIENT_INFORMATION'.\n\n"
            f"Contexto:\n{context_str}\n\n"
            f"Consulta del usuario:\n{query}\n\n"
            "Respuesta:"
        )

        # 5. LLM Synthesis
        answer_text = self.llm.generate_answer(prompt)

        return ChatResponseDTO(
            query=query,
            answer=answer_text,
            max_score=round(max_score, 4),
            threshold=threshold,
            guardrail_passed=True,
            sources=citations,
        )
