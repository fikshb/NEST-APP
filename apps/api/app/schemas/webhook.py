from pydantic import BaseModel


class WebhookCommand(BaseModel):
    command: str
    deal_id: str | None = None
    tenant_id: str | None = None
    unit_id: str | None = None
    params: dict | None = None


class WebhookResponse(BaseModel):
    success: bool
    message: str
    data: dict | None = None
