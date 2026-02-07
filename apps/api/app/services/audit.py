"""Audit logging service — append-only."""
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_action(
    db: Session,
    *,
    action: str,
    summary: str,
    deal_id: str | None = None,
    channel: str = "WEB",
    executor: str = "WEB",
    metadata: dict | None = None,
) -> AuditLog:
    entry = AuditLog(
        deal_id=deal_id,
        actor="ADMIN",
        channel=channel,
        executor=executor,
        action=action,
        summary=summary,
        metadata_json=metadata,
    )
    db.add(entry)
    db.flush()
    return entry
