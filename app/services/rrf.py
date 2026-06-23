import uuid
from dataclasses import dataclass

RRF_K = 60  # standard constant — dampens the impact of very high ranks


@dataclass
class RRFCandidate:
    chunk_id: uuid.UUID
    document_title: str
    page_number: int | None
    content: str
    rrf_score: float


def reciprocal_rank_fusion(
    vector_results: list,   # list of (Chunk, doc_title, distance) rows
    bm25_results: list,     # list of BM25Result
) -> list[RRFCandidate]:
    scores: dict[uuid.UUID, float] = {}
    meta: dict[uuid.UUID, tuple] = {}

    for rank, (chunk, doc_title, _dist) in enumerate(vector_results):
        scores[chunk.id] = scores.get(chunk.id, 0) + 1 / (RRF_K + rank + 1)
        meta[chunk.id] = (doc_title, chunk.page_number, chunk.content)

    for rank, result in enumerate(bm25_results):
        scores[result.chunk_id] = scores.get(result.chunk_id, 0) + 1 / (RRF_K + rank + 1)
        meta[result.chunk_id] = (result.document_title, result.page_number, result.content)

    return [
        RRFCandidate(
            chunk_id=chunk_id,
            document_title=meta[chunk_id][0],
            page_number=meta[chunk_id][1],
            content=meta[chunk_id][2],
            rrf_score=score,
        )
        for chunk_id, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)
    ]
