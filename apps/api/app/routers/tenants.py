from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse
from app.services.audit import log_action

router = APIRouter(prefix="/tenants", tags=["Tenants"])


@router.get("", response_model=list[TenantResponse])
def list_tenants(
    include_archived: bool = False,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Tenant)
    if not include_archived:
        q = q.filter(Tenant.is_archived == False)
    if search:
        q = q.filter(Tenant.full_name.ilike(f"%{search}%"))
    return q.order_by(Tenant.created_at.desc()).all()


@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant(tenant_id: str, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(404, "Tenant not found.")
    return tenant


@router.post("", response_model=TenantResponse, status_code=201)
def create_tenant(data: TenantCreate, db: Session = Depends(get_db)):
    tenant = Tenant(**data.model_dump())
    db.add(tenant)
    log_action(db, action="CREATE_TENANT", summary=f"Created tenant: {tenant.full_name}")
    db.commit()
    db.refresh(tenant)
    return tenant


@router.put("/{tenant_id}", response_model=TenantResponse)
def update_tenant(tenant_id: str, data: TenantUpdate, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(404, "Tenant not found.")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(tenant, field, value)
    log_action(db, action="UPDATE_TENANT", summary=f"Updated tenant: {tenant.full_name}")
    db.commit()
    db.refresh(tenant)
    return tenant


@router.post("/{tenant_id}/archive", response_model=TenantResponse)
def archive_tenant(tenant_id: str, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(404, "Tenant not found.")
    tenant.is_archived = True
    log_action(db, action="UPDATE_TENANT", summary=f"Archived tenant: {tenant.full_name}")
    db.commit()
    db.refresh(tenant)
    return tenant
