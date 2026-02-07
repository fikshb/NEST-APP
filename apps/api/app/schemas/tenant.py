from pydantic import BaseModel, EmailStr
from datetime import datetime


class TenantCreate(BaseModel):
    full_name: str
    phone: str
    email: str
    company_name: str | None = None
    notes: str | None = None


class TenantUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    email: str | None = None
    company_name: str | None = None
    notes: str | None = None


class TenantResponse(BaseModel):
    id: str
    full_name: str
    phone: str
    email: str
    company_name: str | None
    notes: str | None
    is_archived: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
