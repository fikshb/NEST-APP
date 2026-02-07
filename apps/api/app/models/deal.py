import uuid
from datetime import datetime, timezone, date
from decimal import Decimal

from sqlalchemy import String, Text, DateTime, Date, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    deal_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("tenants.id"), nullable=False)
    unit_id: Mapped[str] = mapped_column(String(36), ForeignKey("units.id"), nullable=False)
    term_type: Mapped[str] = mapped_column(String(20), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    list_price: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    deal_price: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(5), default="IDR")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="DRAFT")
    current_step: Mapped[str] = mapped_column(String(50), nullable=False, default="SELECT_UNIT")
    blocked_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    invoice_requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    tenant = relationship("Tenant", back_populates="deals")
    unit = relationship("Unit", back_populates="deals")
    documents = relationship("Document", back_populates="deal", cascade="all, delete-orphan")
    finance_attachments = relationship("FinanceAttachment", back_populates="deal", cascade="all, delete-orphan")
