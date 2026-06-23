import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import Chunk
from app.models.document import Document
from app.services.embedding_service import embed_texts
from app.services.parsing import extract_text, extract_text_by_page, split_text


async def ingest_document(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    filename: str,
    content: bytes,
    mime_type: str,
) -> tuple[Document, int]:
    if mime_type == "application/pdf":
        pages = extract_text_by_page(content)
        page_chunks: list[tuple[str, int]] = [
            (chunk_text, page_num)
            for page_num, page_text in pages
            for chunk_text in split_text(page_text)
        ]
        chunk_texts = [c for c, _ in page_chunks]
        page_numbers: list[int | None] = [p for _, p in page_chunks]
    else:
        chunk_texts = split_text(extract_text(content, mime_type))
        page_numbers = [None] * len(chunk_texts)

    embeddings = await embed_texts(chunk_texts)

    document = Document(tenant_id=tenant_id, title=filename, mime_type=mime_type)
    db.add(document)
    await db.flush()

    chunks = [
        Chunk(
            tenant_id=tenant_id,
            document_id=document.id,
            content=chunk_texts[i],
            chunk_index=i,
            page_number=page_numbers[i],
            embedding=embeddings[i],
        )
        for i in range(len(chunk_texts))
    ]
    db.add_all(chunks)
    await db.commit()
    await db.refresh(document)

    return document, len(chunks)
