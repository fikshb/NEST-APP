from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class UnitCreate(BaseModel):
    unit_code: str
    unit_type: str = "Standard"
    notes: str | None = None
    daily_price: Decimal | None = None
    monthly_price: Decimal | None = None
    six_month_price: Decimal | None = None
    twelve_month_price: Decimal | None = None
    currency: str = "IDR"


class UnitUpdate(BaseModel):
    unit_code: str | None = None
    unit_type: str | None = None
    notes: str | None = None
    daily_price: Decimal | None = None
    monthly_price: Decimal | None = None
    six_month_price: Decimal | None = None
    twelve_month_price: Decimal | None = None


class UnitResponse(BaseModel):
    id: str
    unit_code: str
    unit_type: str
    status: str
    notes: str | None
    daily_price: Decimal | None
    monthly_price: Decimal | None
    six_month_price: Decimal | None
    twelve_month_price: Decimal | None
    currency: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
