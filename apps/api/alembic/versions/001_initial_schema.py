"""Initial schema

Revision ID: 001
Revises: None
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tenants
    op.create_table(
        "tenants",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(50), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("company_name", sa.String(255), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("is_archived", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Units
    op.create_table(
        "units",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("unit_code", sa.String(20), unique=True, nullable=False),
        sa.Column("unit_type", sa.String(50), nullable=False, server_default="Standard"),
        sa.Column("status", sa.String(20), nullable=False, server_default="AVAILABLE"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("daily_price", sa.Numeric(15, 2), nullable=True),
        sa.Column("monthly_price", sa.Numeric(15, 2), nullable=True),
        sa.Column("six_month_price", sa.Numeric(15, 2), nullable=True),
        sa.Column("twelve_month_price", sa.Numeric(15, 2), nullable=True),
        sa.Column("currency", sa.String(5), server_default="IDR"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Deals
    op.create_table(
        "deals",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("deal_code", sa.String(30), unique=True, nullable=False),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("unit_id", sa.String(36), sa.ForeignKey("units.id"), nullable=False),
        sa.Column("term_type", sa.String(20), nullable=False),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=True),
        sa.Column("list_price", sa.Numeric(15, 2), nullable=False),
        sa.Column("deal_price", sa.Numeric(15, 2), nullable=False),
        sa.Column("currency", sa.String(5), server_default="IDR"),
        sa.Column("status", sa.String(30), nullable=False, server_default="DRAFT"),
        sa.Column("current_step", sa.String(50), nullable=False, server_default="SELECT_UNIT"),
        sa.Column("blocked_reason", sa.Text, nullable=True),
        sa.Column("invoice_requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancellation_reason", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Documents (system-generated, per deal)
    op.create_table(
        "documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("deal_id", sa.String(36), sa.ForeignKey("deals.id"), nullable=False),
        sa.Column("doc_type", sa.String(30), nullable=False),
        sa.Column("latest_version", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Document versions
    op.create_table(
        "document_versions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("document_id", sa.String(36), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("version_no", sa.Integer, nullable=False),
        sa.Column("html_path", sa.String(500), nullable=False),
        sa.Column("pdf_path", sa.String(500), nullable=False),
        sa.Column("signatory_name", sa.String(255), nullable=True),
        sa.Column("signatory_title", sa.String(255), nullable=True),
        sa.Column("channel", sa.String(20), server_default="WEB"),
        sa.Column("is_latest", sa.Boolean, server_default=sa.text("true")),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Static documents (catalog, pricelist)
    op.create_table(
        "static_documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("doc_type", sa.String(20), unique=True, nullable=False),
        sa.Column("active_version_id", sa.String(36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Static document versions
    op.create_table(
        "static_document_versions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("static_document_id", sa.String(36), sa.ForeignKey("static_documents.id"), nullable=False),
        sa.Column("version_no", sa.Integer, nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("false")),
    )

    # Finance attachments
    op.create_table(
        "finance_attachments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("deal_id", sa.String(36), sa.ForeignKey("deals.id"), nullable=False),
        sa.Column("attachment_type", sa.String(20), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("channel", sa.String(20), server_default="WEB"),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # App settings (single row)
    op.create_table(
        "app_settings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("company_legal_name", sa.String(255), server_default="NEST Serviced Apartment"),
        sa.Column("company_address", sa.Text, server_default=""),
        sa.Column("logo_path", sa.String(500), nullable=True),
        sa.Column("signatory_name", sa.String(255), server_default=""),
        sa.Column("signatory_title", sa.String(255), server_default=""),
        sa.Column("signature_image_path", sa.String(500), nullable=True),
        sa.Column("finance_email", sa.String(255), server_default="finance@example.com"),
        sa.Column("bot_whatsapp_number", sa.String(50), server_default=""),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Audit logs (append-only)
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("deal_id", sa.String(36), nullable=True),
        sa.Column("actor", sa.String(50), server_default="ADMIN"),
        sa.Column("channel", sa.String(20), server_default="WEB"),
        sa.Column("executor", sa.String(50), server_default="WEB"),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("summary", sa.Text, nullable=False),
        sa.Column("metadata", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Indexes
    op.create_index("ix_deals_status", "deals", ["status"])
    op.create_index("ix_deals_tenant_id", "deals", ["tenant_id"])
    op.create_index("ix_deals_unit_id", "deals", ["unit_id"])
    op.create_index("ix_documents_deal_id", "documents", ["deal_id"])
    op.create_index("ix_audit_logs_deal_id", "audit_logs", ["deal_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("app_settings")
    op.drop_table("finance_attachments")
    op.drop_table("static_document_versions")
    op.drop_table("static_documents")
    op.drop_table("document_versions")
    op.drop_table("documents")
    op.drop_table("deals")
    op.drop_table("units")
    op.drop_table("tenants")
