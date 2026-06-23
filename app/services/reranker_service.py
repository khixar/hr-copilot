from dataclasses import dataclass

import cohere

from app.core.config import settings

_client: cohere.AsyncClientV2 | None = None

RERANK_MODEL = "rerank-english-v3.0"


def get_client() -> cohere.AsyncClientV2:
    global _client
    if _client is None:
        _client = cohere.AsyncClientV2(api_key=settings.COHERE_API_KEY)
    return _client


@dataclass
class RankedResult:
    index: int
    relevance_score: float


async def rerank(query: str, documents: list[str], top_n: int) -> list[RankedResult]:
    response = await get_client().rerank(
        model=RERANK_MODEL,
        query=query,
        documents=documents,
        top_n=top_n,
    )
    return [
        RankedResult(index=r.index, relevance_score=r.relevance_score)
        for r in response.results
    ]
