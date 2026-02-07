"""Journey state machine — enforces sequential step progression."""
import sys
import os

# Add packages to path for shared constants
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "packages", "shared"))

from sqlalchemy.orm import Session

from app.models.deal import Deal
from app.models.document import Document
from app.models.finance_attachment import FinanceAttachment

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

STEP_DOCUMENT_MAP = {
    "GENERATE_BOOKING_CONFIRMATION": "BOOKING_CONFIRMATION",
    "GENERATE_LOO_DRAFT": "LOO_DRAFT",
    "FINALIZE_LOO": "LOO_FINAL",
    "GENERATE_LEASE_AGREEMENT": "LEASE_AGREEMENT",
    "GENERATE_OFFICIAL_CONFIRMATION": "OFFICIAL_CONFIRMATION",
    "GENERATE_MOVE_IN": "MOVE_IN_CONFIRMATION",
    "GENERATE_HANDOVER": "UNIT_HANDOVER",
}

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


def get_journey_steps(deal_type: str) -> list[str]:
    if deal_type == "DAILY":
        return DAILY_JOURNEY_STEPS
    return MONTHLY_JOURNEY_STEPS


def get_current_step_index(deal: Deal) -> int:
    steps = get_journey_steps(deal.term_type)
    try:
        return steps.index(deal.current_step)
    except ValueError:
        return 0


def can_progress(deal: Deal, db: Session) -> tuple[bool, str | None]:
    """Check if a deal can progress to the next step. Returns (can_progress, blocking_reason)."""
    if deal.status == "CANCELLED":
        return False, "This deal has been cancelled."
    if deal.status == "COMPLETED":
        return False, "This deal is already completed."

    steps = get_journey_steps(deal.term_type)
    current_idx = get_current_step_index(deal)

    if current_idx >= len(steps) - 1:
        return False, "All steps are complete."

    current_step = deal.current_step

    # Check if current step requires a document that hasn't been generated
    if current_step in STEP_DOCUMENT_MAP:
        doc_type = STEP_DOCUMENT_MAP[current_step]
        doc = db.query(Document).filter(
            Document.deal_id == deal.id,
            Document.doc_type == doc_type,
        ).first()
        if not doc or doc.latest_version == 0:
            label = JOURNEY_STEP_LABELS.get(current_step, current_step)
            return False, f"Action required: {label} to continue."

    # Check upload invoice step
    if current_step == "UPLOAD_INVOICE":
        attachment = db.query(FinanceAttachment).filter(
            FinanceAttachment.deal_id == deal.id,
            FinanceAttachment.attachment_type == "INVOICE",
        ).first()
        if not attachment:
            return False, "Action required: Upload Invoice to continue."

    # Check request invoice step
    if current_step == "REQUEST_INVOICE":
        if not deal.invoice_requested_at:
            return False, "Action required: Request Invoice to continue."

    return True, None


def advance_step(deal: Deal, db: Session) -> str:
    """Advance the deal to the next journey step. Returns the new step."""
    steps = get_journey_steps(deal.term_type)
    current_idx = get_current_step_index(deal)
    next_idx = current_idx + 1

    if next_idx >= len(steps):
        return deal.current_step

    new_step = steps[next_idx]
    deal.current_step = new_step

    # Update deal status based on step
    if new_step == "DEAL_CLOSED":
        deal.status = "COMPLETED"
    elif new_step == "REQUEST_INVOICE":
        deal.status = "IN_PROGRESS"
    elif new_step == "UPLOAD_INVOICE":
        deal.status = "INVOICE_REQUESTED"
    else:
        deal.status = "IN_PROGRESS"

    deal.blocked_reason = None
    db.flush()
    return new_step


def get_journey_status(deal: Deal, db: Session) -> list[dict]:
    """Return the full journey status with step completion info."""
    steps = get_journey_steps(deal.term_type)
    current_idx = get_current_step_index(deal)
    result = []

    for i, step in enumerate(steps):
        status = "completed" if i < current_idx else ("current" if i == current_idx else "pending")
        entry = {
            "step": step,
            "label": JOURNEY_STEP_LABELS.get(step, step),
            "index": i,
            "status": status,
        }

        # Add blocking info for current step
        if status == "current" and deal.status != "CANCELLED":
            can_go, reason = can_progress(deal, db)
            entry["can_progress"] = can_go
            entry["blocked_reason"] = reason
        else:
            entry["can_progress"] = False
            entry["blocked_reason"] = None

        result.append(entry)

    return result
