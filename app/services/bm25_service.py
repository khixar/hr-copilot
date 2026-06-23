import uuid
from dataclasses import dataclass

from rank_bm25 import BM25Okapi
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import Chunk
from app.models.document import Document


@dataclass
class BM25Result:
    chunk_id: uuid.UUID
    document_title: str
    page_number: int | None
    content: str
    score: float


def _tokenize(text: str) -> list[str]:
    return text.lower().split()


async def bm25_search(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    query: str,
    top_k: int,
) -> list[BM25Result]:
    rows = await db.execute(
        select(Chunk, Document.title)
        .join(Document, Chunk.document_id == Document.id)
        .where(Chunk.tenant_id == tenant_id)
    )
    all_chunks = rows.all()

    if not all_chunks:
        return []

    corpus = [_tokenize(chunk.content) for chunk, _ in all_chunks]
    bm25 = BM25Okapi(corpus)
    scores = bm25.get_scores(_tokenize(query))

    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]

    return [
        BM25Result(
            chunk_id=all_chunks[i][0].id,
            document_title=all_chunks[i][1],
            page_number=all_chunks[i][0].page_number,
            content=all_chunks[i][0].content,
            score=float(score),
        )
        for i, score in ranked
        if score > 0
    ]
