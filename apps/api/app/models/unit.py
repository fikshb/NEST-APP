import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import String, Text, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Unit(Base):
    __tablename__ = "units"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    unit_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    unit_type: Mapped[str] = mapped_column(String(50), nullable=False, default="Standard")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="AVAILABLE")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    daily_price: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    monthly_price: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    six_month_price: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    twelve_month_price: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(5), default="IDR")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    deals = relationship("Deal", back_populates="unit")
