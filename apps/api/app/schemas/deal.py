from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from app.schemas.tenant import TenantResponse
from app.schemas.unit import UnitResponse


class DealCreate(BaseModel):
    tenant_id: str
    unit_id: str
    term_type: str
    start_date: date
    end_date: date | None = None
    currency: str = "IDR"


class DealUpdate(BaseModel):
    start_date: date | None = None
    end_date: date | None = None


class DealSetPriceRequest(BaseModel):
    deal_price: Decimal


class DealSetMoveInRequest(BaseModel):
    move_in_date: date
    move_in_notes: str = ""


class DealResponse(BaseModel):
    id: str
    deal_code: str
    tenant_id: str
    unit_id: str
    term_type: str
    start_date: date
    end_date: date | None
    initial_price: Decimal
    deal_price: Decimal | None
    currency: str
    status: str
    current_step: str
    blocked_reason: str | None
    invoice_requested_at: datetime | None
    cancelled_at: datetime | None
    cancellation_reason: str | None
    move_in_date: date | None
    move_in_notes: str | None
    created_at: datetime
    updated_at: datetime
    tenant: TenantResponse | None = None
    unit: UnitResponse | None = None

    model_config = {"from_attributes": True}


class DealCancelRequest(BaseModel):
    reason: str


class DealOverrideRequest(BaseModel):
    reason: str
    target_step: str


class DealActionResponse(BaseModel):
    success: bool
    message: str
    deal: DealResponse | None = None
