from pydantic import BaseModel, Field
from typing import List, Optional


class CitationResponse(BaseModel):
    document: str
    page: int
    score: float
    snippet: str


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Pregunta del usuario")
    similarity_threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Umbral de confianza del guardrail")
    limit: Optional[int] = Field(None, ge=1, le=20, description="Cantidad máxima de fuentes a recuperar")


class ChatResponse(BaseModel):
    query: str
    answer: str
    max_score: float
    threshold: float
    guardrail_passed: bool
    sources: List[CitationResponse] = []
    message: Optional[str] = None


class DocumentResponse(BaseModel):
    name: str
    in_storage: bool = True
    in_vector_store: bool = True


class DocumentListResponse(BaseModel):
    total: int
    documents: List[DocumentResponse]


class UploadResponse(BaseModel):
    uploaded: List[str]
    total_chunks: int
    message: str


class DeleteResponse(BaseModel):
    document_name: str
    deleted: bool
    message: str


class HealthResponse(BaseModel):
    status: str
    version: str
    collection: str
