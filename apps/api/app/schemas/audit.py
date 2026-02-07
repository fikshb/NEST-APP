from pydantic import BaseModel
from datetime import datetime


class AuditLogResponse(BaseModel):
    id: str
    deal_id: str | None
    actor: str
    channel: str
    executor: str
    action: str
    summary: str
    metadata_json: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogQuery(BaseModel):
    deal_id: str | None = None
    action: str | None = None
    channel: str | None = None
    page: int = 1
    size: int = 50
