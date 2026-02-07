"""
NestApp Shared Constants — Python mirror.
Keep in sync with constants.ts (single source of truth).
"""
from enum import Enum


class DealType(str, Enum):
    DAILY = "DAILY"
    MONTHLY = "MONTHLY"
    SIX_MONTHS = "SIX_MONTHS"
    TWELVE_MONTHS = "TWELVE_MONTHS"


DEAL_TYPE_LABELS = {
    DealType.DAILY: "Daily",
    DealType.MONTHLY: "Monthly",
    DealType.SIX_MONTHS: "6 Months",
    DealType.TWELVE_MONTHS: "12 Months",
}


class DealStatus(str, Enum):
    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    INVOICE_REQUESTED = "INVOICE_REQUESTED"
    INVOICE_UPLOADED = "INVOICE_UPLOADED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class UnitStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    OCCUPIED = "OCCUPIED"


class DocumentType(str, Enum):
    BOOKING_CONFIRMATION = "BOOKING_CONFIRMATION"
    LOO_DRAFT = "LOO_DRAFT"
    LOO_FINAL = "LOO_FINAL"
    LEASE_AGREEMENT = "LEASE_AGREEMENT"
    OFFICIAL_CONFIRMATION = "OFFICIAL_CONFIRMATION"
    MOVE_IN_CONFIRMATION = "MOVE_IN_CONFIRMATION"
    UNIT_HANDOVER = "UNIT_HANDOVER"


DOCUMENT_TYPE_LABELS = {
    DocumentType.BOOKING_CONFIRMATION: "Booking Confirmation",
    DocumentType.LOO_DRAFT: "Letter of Offer – Draft",
    DocumentType.LOO_FINAL: "Letter of Offer – Final",
    DocumentType.LEASE_AGREEMENT: "Lease Agreement",
    DocumentType.OFFICIAL_CONFIRMATION: "Official Confirmation Letter",
    DocumentType.MOVE_IN_CONFIRMATION: "Move-in Confirmation",
    DocumentType.UNIT_HANDOVER: "Unit Handover Certificate",
}


class StaticDocumentType(str, Enum):
    CATALOG = "CATALOG"
    PRICELIST = "PRICELIST"


class Channel(str, Enum):
    WEB = "WEB"
    WHATSAPP = "WHATSAPP"


class AuditAction(str, Enum):
    CREATE_DEAL = "CREATE_DEAL"
    UPDATE_DEAL = "UPDATE_DEAL"
    PROGRESS_DEAL = "PROGRESS_DEAL"
    CANCEL_DEAL = "CANCEL_DEAL"
    EMERGENCY_OVERRIDE = "EMERGENCY_OVERRIDE"
    GENERATE_DOCUMENT = "GENERATE_DOCUMENT"
    REQUEST_INVOICE = "REQUEST_INVOICE"
    UPLOAD_INVOICE = "UPLOAD_INVOICE"
    CREATE_TENANT = "CREATE_TENANT"
    UPDATE_TENANT = "UPDATE_TENANT"
    CREATE_UNIT = "CREATE_UNIT"
    UPDATE_UNIT = "UPDATE_UNIT"
    UPLOAD_STATIC_DOCUMENT = "UPLOAD_STATIC_DOCUMENT"
    ACTIVATE_STATIC_DOCUMENT = "ACTIVATE_STATIC_DOCUMENT"
    UPDATE_SETTINGS = "UPDATE_SETTINGS"


class FinanceAttachmentType(str, Enum):
    INVOICE = "INVOICE"
    RECEIPT = "RECEIPT"


# ── Journey Definitions ──

DAILY_JOURNEY_STEPS = [
    "SELECT_UNIT",
    "GENERATE_BOOKING_CONFIRMATION",
    "GENERATE_OFFICIAL_CONFIRMATION",
    "REQUEST_INVOICE",
    "UPLOAD_INVOICE",
    "GENERATE_HANDOVER",
    "DEAL_CLOSED",
]

MONTHLY_JOURNEY_STEPS = [
    "SELECT_UNIT",
    "GENERATE_LOO_DRAFT",
    "FINALIZE_LOO",
    "GENERATE_LEASE_AGREEMENT",
    "GENERATE_OFFICIAL_CONFIRMATION",
    "REQUEST_INVOICE",
    "UPLOAD_INVOICE",
    "GENERATE_MOVE_IN",
    "GENERATE_HANDOVER",
    "DEAL_CLOSED",
]

JOURNEY_STEP_LABELS = {
    "SELECT_UNIT": "Select Unit",
    "GENERATE_BOOKING_CONFIRMATION": "Generate Booking Confirmation",
    "GENERATE_OFFICIAL_CONFIRMATION": "Generate Official Confirmation Letter",
    "REQUEST_INVOICE": "Request Invoice",
    "UPLOAD_INVOICE": "Upload Invoice",
    "GENERATE_HANDOVER": "Generate Unit Handover Certificate",
    "DEAL_CLOSED": "Deal Closed",
    "GENERATE_LOO_DRAFT": "Generate Offer (LOO Draft)",
    "FINALIZE_LOO": "Finalize Offer (LOO Final)",
    "GENERATE_LEASE_AGREEMENT": "Generate Lease Agreement",
    "GENERATE_MOVE_IN": "Generate Move-in Confirmation",
}

# Map journey steps to document types
STEP_DOCUMENT_MAP = {
    "GENERATE_BOOKING_CONFIRMATION": DocumentType.BOOKING_CONFIRMATION,
    "GENERATE_LOO_DRAFT": DocumentType.LOO_DRAFT,
    "FINALIZE_LOO": DocumentType.LOO_FINAL,
    "GENERATE_LEASE_AGREEMENT": DocumentType.LEASE_AGREEMENT,
    "GENERATE_OFFICIAL_CONFIRMATION": DocumentType.OFFICIAL_CONFIRMATION,
    "GENERATE_MOVE_IN": DocumentType.MOVE_IN_CONFIRMATION,
    "GENERATE_HANDOVER": DocumentType.UNIT_HANDOVER,
}


def get_journey_steps(deal_type: DealType) -> list[str]:
    """Return the ordered journey steps for a given deal type."""
    if deal_type == DealType.DAILY:
        return DAILY_JOURNEY_STEPS
    return MONTHLY_JOURNEY_STEPS
