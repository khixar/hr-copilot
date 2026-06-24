import uuid
from typing import TypedDict

from app.schemas.query import SourceChunk
from app.services.rrf import RRFCandidate


class AgentState(TypedDict):
    question: str
    tenant_id: uuid.UUID
    retrieved_chunks: list[RRFCandidate]
    retrieval_empty: bool
    should_escalate: bool
    escalation_reason: str | None
    answer: str | None
    sources: list[SourceChunk]
