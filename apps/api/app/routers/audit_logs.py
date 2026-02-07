import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.audit_log import AuditLog
from app.schemas.audit import AuditLogResponse

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("", response_model=list[AuditLogResponse])
def list_audit_logs(
    deal_id: str | None = None,
    action: str | None = None,
    channel: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(AuditLog)
    if deal_id:
        q = q.filter(AuditLog.deal_id == deal_id)
    if action:
        q = q.filter(AuditLog.action == action)
    if channel:
        q = q.filter(AuditLog.channel == channel)

    return q.order_by(AuditLog.created_at.desc()).offset((page - 1) * size).limit(size).all()


@router.get("/export")
def export_audit_logs(
    deal_id: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(AuditLog)
    if deal_id:
        q = q.filter(AuditLog.deal_id == deal_id)
    logs = q.order_by(AuditLog.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Deal ID", "Actor", "Channel", "Executor", "Action", "Summary", "Created At"])
    for log in logs:
        writer.writerow([
            log.id, log.deal_id, log.actor, log.channel, log.executor,
            log.action, log.summary, log.created_at.isoformat() if log.created_at else "",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=audit_logs_{datetime.utcnow().strftime('%Y%m%d')}.csv"},
    )
