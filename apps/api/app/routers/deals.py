import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.deal import Deal
from app.models.unit import Unit
from app.models.finance_attachment import FinanceAttachment
from app.schemas.deal import DealCreate, DealUpdate, DealResponse, DealCancelRequest, DealOverrideRequest, DealActionResponse, DealSetPriceRequest, DealSetMoveInRequest
from app.services.audit import log_action
from app.services.journey import get_journey_steps, get_journey_status, advance_step, can_progress, STEP_DOCUMENT_MAP
from app.services.document_generator import generate_document
from app.services.email import send_invoice_request_email
from app.models.document import Document
from app.models.settings import AppSettings
from app.config import settings as app_config

import os

router = APIRouter(prefix="/deals", tags=["Deals"])

TERM_PRICE_MAP = {
    "DAILY": "daily_price",
    "MONTHLY": "monthly_price",
    "SIX_MONTHS": "six_month_price",
    "TWELVE_MONTHS": "twelve_month_price",
}


def _generate_deal_code(db: Session) -> str:
    count = db.query(Deal).count() + 1
    return f"NEST-{count:05d}"


def _load_deal(deal_id: str, db: Session) -> Deal:
    deal = db.query(Deal).options(
        joinedload(Deal.tenant),
        joinedload(Deal.unit),
    ).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(404, "Deal not found.")
    return deal


def _get_unit_price(unit: Unit, term_type: str):
    """Get the unit price based on term type."""
    price_field = TERM_PRICE_MAP.get(term_type)
    if not price_field:
        raise HTTPException(400, f"Invalid term type: {term_type}")
    price = getattr(unit, price_field, None)
    if price is None:
        raise HTTPException(400, f"Unit {unit.unit_code} does not have a {term_type.lower().replace('_', ' ')} price configured.")
    return price


@router.get("", response_model=list[DealResponse])
def list_deals(
    status: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Deal).options(joinedload(Deal.tenant), joinedload(Deal.unit))
    if status:
        q = q.filter(Deal.status == status)
    return q.order_by(Deal.created_at.desc()).all()


@router.get("/{deal_id}", response_model=DealResponse)
def get_deal(deal_id: str, db: Session = Depends(get_db)):
    return _load_deal(deal_id, db)


@router.get("/{deal_id}/journey")
def get_deal_journey(deal_id: str, db: Session = Depends(get_db)):
    deal = _load_deal(deal_id, db)
    return {
        "deal_id": deal.id,
        "term_type": deal.term_type,
        "current_step": deal.current_step,
        "status": deal.status,
        "steps": get_journey_status(deal, db),
    }


@router.post("", response_model=DealResponse, status_code=201)
def create_deal(data: DealCreate, db: Session = Depends(get_db)):
    # Validate unit exists and is available
    unit = db.query(Unit).filter(Unit.id == data.unit_id).first()
    if not unit:
        raise HTTPException(404, "Unit not found.")
    if unit.status != "AVAILABLE":
        raise HTTPException(409, "This unit is not available for booking.")

    # Auto-set initial_price from unit pricing
    initial_price = _get_unit_price(unit, data.term_type)

    deal_code = _generate_deal_code(db)
    deal = Deal(
        deal_code=deal_code,
        tenant_id=data.tenant_id,
        unit_id=data.unit_id,
        term_type=data.term_type,
        start_date=data.start_date,
        end_date=data.end_date,
        initial_price=initial_price,
        currency=data.currency,
    )
    # First step is SELECT_UNIT which is done by creating the deal
    deal.current_step = "SELECT_UNIT"
    deal.status = "DRAFT"
    db.add(deal)

    # Reserve the unit
    unit.status = "RESERVED"

    log_action(db, action="CREATE_DEAL", summary=f"Created deal {deal_code}", deal_id=deal.id)

    # Auto-advance past SELECT_UNIT since unit is selected by creating the deal
    steps = get_journey_steps(deal.term_type)
    if len(steps) > 1:
        deal.current_step = steps[1]
        deal.status = "IN_PROGRESS"

    db.commit()
    db.refresh(deal)
    return _load_deal(deal.id, db)


@router.patch("/{deal_id}", response_model=DealResponse)
def update_deal(deal_id: str, data: DealUpdate, db: Session = Depends(get_db)):
    deal = _load_deal(deal_id, db)
    if deal.status == "CANCELLED":
        raise HTTPException(409, "This deal has been cancelled and cannot be modified.")
    if deal.status == "COMPLETED":
        raise HTTPException(409, "This deal is completed and cannot be modified.")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(deal, field, value)
    log_action(db, action="UPDATE_DEAL", summary=f"Updated deal {deal.deal_code}", deal_id=deal.id)
    db.commit()
    db.refresh(deal)
    return deal


# ── Deal Actions ──

@router.post("/{deal_id}/actions/set-deal-price", response_model=DealActionResponse)
def action_set_deal_price(deal_id: str, data: DealSetPriceRequest, db: Session = Depends(get_db)):
    """Set the negotiated deal price. Available at FINALIZE_LOO or GENERATE_BOOKING_CONFIRMATION step."""
    deal = _load_deal(deal_id, db)
    if deal.status in ("CANCELLED", "COMPLETED"):
        raise HTTPException(409, "This deal cannot be modified.")
    if deal.current_step not in ("FINALIZE_LOO", "GENERATE_BOOKING_CONFIRMATION"):
        raise HTTPException(400, "Deal price can only be set at the Booking Confirmation or Finalize LOO step.")

    deal.deal_price = data.deal_price
    log_action(
        db,
        action="SET_DEAL_PRICE",
        summary=f"Negotiated price set to {data.deal_price} for deal {deal.deal_code}",
        deal_id=deal.id,
        metadata={"initial_price": str(deal.initial_price), "deal_price": str(data.deal_price)},
    )
    db.commit()
    db.refresh(deal)
    refreshed = _load_deal(deal.id, db)
    return DealActionResponse(success=True, message="Deal price updated.", deal=DealResponse.model_validate(refreshed))


@router.post("/{deal_id}/actions/set-move-in-details", response_model=DealActionResponse)
def action_set_move_in_details(deal_id: str, data: DealSetMoveInRequest, db: Session = Depends(get_db)):
    """Set move-in date and items list. Available at GENERATE_MOVE_IN step."""
    deal = _load_deal(deal_id, db)
    if deal.status in ("CANCELLED", "COMPLETED"):
        raise HTTPException(409, "This deal cannot be modified.")
    if deal.current_step != "GENERATE_MOVE_IN":
        raise HTTPException(400, "Move-in details can only be set at the Move-in Confirmation step.")

    deal.move_in_date = data.move_in_date
    deal.move_in_notes = data.move_in_notes
    log_action(
        db,
        action="SET_MOVE_IN_DETAILS",
        summary=f"Move-in details set for deal {deal.deal_code}: date={data.move_in_date}",
        deal_id=deal.id,
        metadata={"move_in_date": str(data.move_in_date), "move_in_notes": data.move_in_notes},
    )
    db.commit()
    db.refresh(deal)
    refreshed = _load_deal(deal.id, db)
    return DealActionResponse(success=True, message="Move-in details saved.", deal=DealResponse.model_validate(refreshed))


@router.post("/{deal_id}/actions/generate-document", response_model=DealActionResponse)
def action_generate_document(deal_id: str, db: Session = Depends(get_db), channel: str = "WEB"):
    deal = _load_deal(deal_id, db)
    if deal.status in ("CANCELLED", "COMPLETED"):
        raise HTTPException(409, "This deal cannot be progressed.")

    current_step = deal.current_step
    if current_step not in STEP_DOCUMENT_MAP:
        raise HTTPException(400, "The current step does not require document generation.")

    # If no deal_price set at document generation, use initial_price as deal_price
    if current_step in ("FINALIZE_LOO", "GENERATE_BOOKING_CONFIRMATION") and deal.deal_price is None:
        deal.deal_price = deal.initial_price

    doc_type = STEP_DOCUMENT_MAP[current_step]
    version = generate_document(db, deal, doc_type, channel=channel)

    log_action(
        db,
        action="GENERATE_DOCUMENT",
        summary=f"Generated {doc_type} v{version.version_no} for deal {deal.deal_code}",
        deal_id=deal.id,
        channel=channel,
        executor="CLAWDBOT" if channel == "WHATSAPP" else "WEB",
    )

    # Advance to next step
    advance_step(deal, db)
    log_action(
        db,
        action="PROGRESS_DEAL",
        summary=f"Advanced deal {deal.deal_code} to step: {deal.current_step}",
        deal_id=deal.id,
        channel=channel,
        executor="CLAWDBOT" if channel == "WHATSAPP" else "WEB",
    )

    db.commit()
    db.refresh(deal)
    refreshed = _load_deal(deal.id, db)
    return DealActionResponse(success=True, message=f"Document generated successfully.", deal=DealResponse.model_validate(refreshed))


@router.post("/{deal_id}/actions/request-invoice", response_model=DealActionResponse)
def action_request_invoice(deal_id: str, db: Session = Depends(get_db), channel: str = "WEB"):
    deal = _load_deal(deal_id, db)
    if deal.current_step != "REQUEST_INVOICE":
        raise HTTPException(400, "This action is not available yet.")

    # Get settings for finance email
    app_settings = db.query(AppSettings).first()
    finance_email = app_settings.finance_email if app_settings else app_config.finance_email

    # Use deal_price if set, otherwise initial_price
    effective_price = deal.deal_price if deal.deal_price is not None else deal.initial_price

    # Find latest document PDF to attach
    pdf_path = None
    latest_doc = db.query(Document).filter(Document.deal_id == deal.id).order_by(Document.created_at.desc()).first()
    if latest_doc and latest_doc.versions:
        latest_version = latest_doc.versions[0]  # ordered desc by version_no
        if latest_version.pdf_path:
            pdf_path = os.path.join(app_config.storage_root, latest_version.pdf_path)

    send_invoice_request_email(
        finance_email=finance_email,
        deal_code=deal.deal_code,
        tenant_name=deal.tenant.full_name,
        unit_code=deal.unit.unit_code,
        amount=str(effective_price),
        currency=deal.currency,
        pdf_path=pdf_path,
    )

    deal.invoice_requested_at = datetime.now(timezone.utc)
    deal.status = "INVOICE_REQUESTED"

    log_action(
        db,
        action="REQUEST_INVOICE",
        summary=f"Invoice requested for deal {deal.deal_code}",
        deal_id=deal.id,
        channel=channel,
        executor="CLAWDBOT" if channel == "WHATSAPP" else "WEB",
    )

    # Advance to UPLOAD_INVOICE
    advance_step(deal, db)

    db.commit()
    db.refresh(deal)
    refreshed = _load_deal(deal.id, db)
    return DealActionResponse(success=True, message="Invoice request sent to finance.", deal=DealResponse.model_validate(refreshed))


@router.post("/{deal_id}/actions/upload-invoice", response_model=DealActionResponse)
def action_upload_invoice(
    deal_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    channel: str = "WEB",
):
    deal = _load_deal(deal_id, db)
    if deal.current_step != "UPLOAD_INVOICE":
        raise HTTPException(400, "This action is not available yet.")

    # Save file
    deal_dir = os.path.join("finance", deal.id)
    file_dir = os.path.join(app_config.storage_root, deal_dir)
    os.makedirs(file_dir, exist_ok=True)

    file_ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "pdf"
    stored_name = f"invoice_{uuid.uuid4().hex[:8]}.{file_ext}"
    file_path = os.path.join(deal_dir, stored_name)
    full_path = os.path.join(app_config.storage_root, file_path)

    with open(full_path, "wb") as f:
        content = file.file.read()
        f.write(content)

    attachment = FinanceAttachment(
        deal_id=deal.id,
        attachment_type="INVOICE",
        file_name=file.filename,
        file_path=file_path,
        channel=channel,
    )
    db.add(attachment)

    deal.status = "INVOICE_UPLOADED"

    log_action(
        db,
        action="UPLOAD_INVOICE",
        summary=f"Invoice uploaded for deal {deal.deal_code}",
        deal_id=deal.id,
        channel=channel,
        executor="CLAWDBOT" if channel == "WHATSAPP" else "WEB",
    )

    advance_step(deal, db)

    db.commit()
    db.refresh(deal)
    refreshed = _load_deal(deal.id, db)
    return DealActionResponse(success=True, message="Invoice uploaded successfully.", deal=DealResponse.model_validate(refreshed))


@router.post("/{deal_id}/actions/close", response_model=DealActionResponse)
def action_close_deal(deal_id: str, db: Session = Depends(get_db)):
    deal = _load_deal(deal_id, db)
    if deal.current_step != "DEAL_CLOSED":
        raise HTTPException(400, "This deal cannot be closed yet. Please complete all steps.")

    deal.status = "COMPLETED"
    # Set unit to OCCUPIED
    unit = db.query(Unit).filter(Unit.id == deal.unit_id).first()
    if unit:
        unit.status = "OCCUPIED"

    log_action(db, action="PROGRESS_DEAL", summary=f"Deal {deal.deal_code} closed", deal_id=deal.id)
    db.commit()
    db.refresh(deal)
    refreshed = _load_deal(deal.id, db)
    return DealActionResponse(success=True, message="Deal closed successfully.", deal=DealResponse.model_validate(refreshed))


@router.post("/{deal_id}/actions/cancel", response_model=DealActionResponse)
def action_cancel_deal(deal_id: str, data: DealCancelRequest, db: Session = Depends(get_db)):
    deal = _load_deal(deal_id, db)
    if deal.status == "CANCELLED":
        raise HTTPException(409, "This deal is already cancelled.")

    deal.status = "CANCELLED"
    deal.cancelled_at = datetime.now(timezone.utc)
    deal.cancellation_reason = data.reason

    # Release unit
    unit = db.query(Unit).filter(Unit.id == deal.unit_id).first()
    if unit and unit.status in ("RESERVED", "OCCUPIED"):
        unit.status = "AVAILABLE"

    log_action(
        db,
        action="CANCEL_DEAL",
        summary=f"Deal {deal.deal_code} cancelled. Reason: {data.reason}",
        deal_id=deal.id,
        metadata={"reason": data.reason},
    )
    db.commit()
    db.refresh(deal)
    refreshed = _load_deal(deal.id, db)
    return DealActionResponse(success=True, message="Deal cancelled.", deal=DealResponse.model_validate(refreshed))


@router.post("/{deal_id}/actions/emergency-override", response_model=DealActionResponse)
def action_emergency_override(
    deal_id: str,
    data: DealOverrideRequest,
    db: Session = Depends(get_db),
    channel: str = "WEB",
):
    """Emergency override — Web UI only, not accessible by bot."""
    if channel == "WHATSAPP":
        raise HTTPException(403, "Emergency override is not accessible via WhatsApp.")

    deal = _load_deal(deal_id, db)
    if deal.status in ("CANCELLED", "COMPLETED"):
        raise HTTPException(409, "Cannot override a cancelled or completed deal.")

    steps = get_journey_steps(deal.term_type)
    if data.target_step not in steps:
        raise HTTPException(400, f"Invalid target step: {data.target_step}")

    old_step = deal.current_step
    deal.current_step = data.target_step
    deal.blocked_reason = None

    if data.target_step == "DEAL_CLOSED":
        deal.status = "COMPLETED"
    else:
        deal.status = "IN_PROGRESS"

    log_action(
        db,
        action="EMERGENCY_OVERRIDE",
        summary=f"Emergency override on deal {deal.deal_code}: {old_step} → {data.target_step}. Reason: {data.reason}",
        deal_id=deal.id,
        metadata={"reason": data.reason, "from_step": old_step, "to_step": data.target_step},
    )
    db.commit()
    db.refresh(deal)
    refreshed = _load_deal(deal.id, db)
    return DealActionResponse(success=True, message="Emergency override applied.", deal=DealResponse.model_validate(refreshed))
