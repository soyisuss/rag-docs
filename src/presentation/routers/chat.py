from fastapi import APIRouter, Depends
from src.presentation.schemas import ChatRequest, ChatResponse, CitationResponse
from src.application.dtos import ChatRequestDTO
from src.application.use_cases.ask_question import AskQuestionUseCase
from src.presentation.dependencies import get_ask_question_use_case

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
def ask_chat(
    payload: ChatRequest,
    use_case: AskQuestionUseCase = Depends(get_ask_question_use_case),
) -> ChatResponse:
    dto = ChatRequestDTO(
        query=payload.query,
        similarity_threshold=payload.similarity_threshold,
        limit=payload.limit,
    )
    result = use_case.execute(dto)

    return ChatResponse(
        query=result.query,
        answer=result.answer,
        max_score=result.max_score,
        threshold=result.threshold,
        guardrail_passed=result.guardrail_passed,
        sources=[
            CitationResponse(
                document=s.document,
                page=s.page,
                score=s.score,
                snippet=s.snippet,
            )
            for s in result.sources
        ],
        message=result.message,
    )
