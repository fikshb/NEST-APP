import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AppSettings(Base):
    __tablename__ = "app_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_legal_name: Mapped[str] = mapped_column(String(255), default="NEST Serviced Apartment")
    company_address: Mapped[str] = mapped_column(Text, default="")
    logo_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    signatory_name: Mapped[str] = mapped_column(String(255), default="")
    signatory_title: Mapped[str] = mapped_column(String(255), default="")
    signature_image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    finance_email: Mapped[str] = mapped_column(String(255), default="finance@example.com")
    bot_whatsapp_number: Mapped[str] = mapped_column(String(50), default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
