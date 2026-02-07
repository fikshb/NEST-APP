from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.unit import Unit
from app.models.deal import Deal
from app.schemas.unit import UnitCreate, UnitUpdate, UnitResponse
from app.services.audit import log_action

router = APIRouter(prefix="/units", tags=["Units"])


@router.get("", response_model=list[UnitResponse])
def list_units(status: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Unit)
    if status:
        q = q.filter(Unit.status == status)
    return q.order_by(Unit.unit_code).all()


@router.get("/{unit_id}", response_model=UnitResponse)
def get_unit(unit_id: str, db: Session = Depends(get_db)):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(404, "Unit not found.")
    return unit


@router.post("", response_model=UnitResponse, status_code=201)
def create_unit(data: UnitCreate, db: Session = Depends(get_db)):
    existing = db.query(Unit).filter(Unit.unit_code == data.unit_code).first()
    if existing:
        raise HTTPException(409, f"Unit code '{data.unit_code}' already exists.")
    unit = Unit(**data.model_dump())
    db.add(unit)
    log_action(db, action="CREATE_UNIT", summary=f"Created unit: {unit.unit_code}")
    db.commit()
    db.refresh(unit)
    return unit


@router.put("/{unit_id}", response_model=UnitResponse)
def update_unit(unit_id: str, data: UnitUpdate, db: Session = Depends(get_db)):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(404, "Unit not found.")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(unit, field, value)
    log_action(db, action="UPDATE_UNIT", summary=f"Updated unit: {unit.unit_code}")
    db.commit()
    db.refresh(unit)
    return unit


@router.delete("/{unit_id}")
def delete_unit(unit_id: str, db: Session = Depends(get_db)):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(404, "Unit not found.")
    # Restrict delete if referenced by deals
    deal_count = db.query(Deal).filter(Deal.unit_id == unit_id).count()
    if deal_count > 0:
        raise HTTPException(409, "Cannot delete unit that is referenced by existing deals.")
    db.delete(unit)
    db.commit()
    return {"success": True, "message": f"Unit {unit.unit_code} deleted."}
