from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.query import QueryRequest, QueryResponse
from app.services.query_service import run_query

router = APIRouter(prefix="/query", tags=["query"])


@router.post("/", response_model=QueryResponse)
async def query(request: QueryRequest, db: AsyncSession = Depends(get_db)):
    return await run_query(
        db=db,
        tenant_id=request.tenant_id,
        question=request.question,
        top_k=request.top_k,
        min_similarity=request.min_similarity,
    )
