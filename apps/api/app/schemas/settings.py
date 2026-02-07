from pydantic import BaseModel
from datetime import datetime


class SettingsUpdate(BaseModel):
    company_legal_name: str | None = None
    company_address: str | None = None
    signatory_name: str | None = None
    signatory_title: str | None = None
    finance_email: str | None = None
    bot_whatsapp_number: str | None = None


class SettingsResponse(BaseModel):
    id: str
    company_legal_name: str
    company_address: str
    logo_path: str | None
    signatory_name: str
    signatory_title: str
    signature_image_path: str | None
    finance_email: str
    bot_whatsapp_number: str
    updated_at: datetime

    model_config = {"from_attributes": True}
