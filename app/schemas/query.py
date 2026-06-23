import uuid

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    tenant_id: uuid.UUID
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    min_similarity: float = Field(default=0.25, ge=0.0, le=1.0)


class SourceChunk(BaseModel):
    document_title: str
    page_number: int | None
    content: str
    rrf_score: float
    relevance_score: float


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
