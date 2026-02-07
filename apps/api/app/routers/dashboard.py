from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.deal import Deal
from app.models.unit import Unit
from app.schemas.dashboard import DashboardSummary, UnitOccupancy, DealStatusChart

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardSummary)
def get_dashboard(db: Session = Depends(get_db)):
    # Deal counts
    in_progress = db.query(func.count(Deal.id)).filter(Deal.status.in_(["DRAFT", "IN_PROGRESS"])).scalar() or 0
    blocked = db.query(func.count(Deal.id)).filter(Deal.blocked_reason.isnot(None), Deal.status != "CANCELLED").scalar() or 0
    awaiting = db.query(func.count(Deal.id)).filter(Deal.status.in_(["INVOICE_REQUESTED", "INVOICE_UPLOADED"])).scalar() or 0
    completed = db.query(func.count(Deal.id)).filter(Deal.status == "COMPLETED").scalar() or 0

    # Unit occupancy
    available = db.query(func.count(Unit.id)).filter(Unit.status == "AVAILABLE").scalar() or 0
    reserved = db.query(func.count(Unit.id)).filter(Unit.status == "RESERVED").scalar() or 0
    occupied = db.query(func.count(Unit.id)).filter(Unit.status == "OCCUPIED").scalar() or 0

    # Deal status chart
    chart_in_progress = db.query(func.count(Deal.id)).filter(Deal.status.in_(["DRAFT", "IN_PROGRESS"])).scalar() or 0
    chart_invoice = db.query(func.count(Deal.id)).filter(Deal.status == "INVOICE_REQUESTED").scalar() or 0
    chart_completed = db.query(func.count(Deal.id)).filter(Deal.status == "COMPLETED").scalar() or 0

    return DashboardSummary(
        deals_in_progress=in_progress,
        deals_blocked=blocked,
        deals_awaiting_action=awaiting,
        deals_completed=completed,
        unit_occupancy=UnitOccupancy(available=available, reserved=reserved, occupied=occupied),
        deal_status_chart=DealStatusChart(in_progress=chart_in_progress, invoice_requested=chart_invoice, completed=chart_completed),
    )
