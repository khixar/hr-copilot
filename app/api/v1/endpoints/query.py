from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.graph import compiled
from app.db.session import get_db
from app.schemas.query import QueryRequest, QueryResponse

router = APIRouter(prefix="/query", tags=["query"])


@router.post("/", response_model=QueryResponse)
async def query(request: QueryRequest, db: AsyncSession = Depends(get_db)):
    result = await compiled.ainvoke(
        {
            "question": request.question,
            "tenant_id": request.tenant_id,
        },
        config={"configurable": {"db": db}},
    )
    return QueryResponse(answer=result["answer"], sources=result["sources"])
