import uuid
from datetime import datetime

from pydantic import BaseModel


class DocumentRead(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    title: str
    source_uri: str | None
    mime_type: str | None
    created_at: datetime
    chunk_count: int = 0

    model_config = {"from_attributes": True}
