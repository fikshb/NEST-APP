"""OpenClaw/ClawdBot webhook integration stub.

All bot commands go through this endpoint, which internally calls
the same deal action logic. Audit logs correctly record channel=WHATSAPP
and executor=CLAWDBOT.
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.schemas.webhook import WebhookCommand, WebhookResponse
from app.services.audit import log_action

router = APIRouter(prefix="/integrations/openclaw", tags=["OpenClaw Integration"])


def verify_bot_token(authorization: str = Header(...)):
    """Validate the bot service token."""
    expected = f"Bearer {settings.openclaw_service_token}"
    if authorization != expected:
        raise HTTPException(401, "Invalid service token.")


@router.post("/webhook", response_model=WebhookResponse, dependencies=[Depends(verify_bot_token)])
def handle_webhook(cmd: WebhookCommand, db: Session = Depends(get_db)):
    """
    Process a bot command. Supported commands:
    - create_deal
    - generate_document
    - request_invoice
    - get_deal_status
    - get_catalog
    - get_pricelist

    This is a stub — it validates the token, logs the command,
    and returns a structured response. The real integration would
    call the same internal service functions.
    """
    log_action(
        db,
        action="PROGRESS_DEAL" if cmd.command.startswith("generate") else "UPDATE_DEAL",
        summary=f"Bot command received: {cmd.command}",
        deal_id=cmd.deal_id,
        channel="WHATSAPP",
        executor="CLAWDBOT",
        metadata={"command": cmd.command, "params": cmd.params},
    )

    # Route commands
    if cmd.command == "create_deal":
        db.commit()
        return WebhookResponse(
            success=True,
            message="Deal creation command received. Use POST /deals with channel=WHATSAPP for full implementation.",
            data={"command": cmd.command},
        )

    elif cmd.command == "generate_document":
        if not cmd.deal_id:
            raise HTTPException(400, "deal_id is required for document generation.")
        db.commit()
        return WebhookResponse(
            success=True,
            message="Document generation command received. Use POST /deals/{id}/actions/generate-document?channel=WHATSAPP.",
            data={"command": cmd.command, "deal_id": cmd.deal_id},
        )

    elif cmd.command == "request_invoice":
        if not cmd.deal_id:
            raise HTTPException(400, "deal_id is required for invoice request.")
        db.commit()
        return WebhookResponse(
            success=True,
            message="Invoice request command received. Use POST /deals/{id}/actions/request-invoice?channel=WHATSAPP.",
            data={"command": cmd.command, "deal_id": cmd.deal_id},
        )

    elif cmd.command == "get_deal_status":
        if not cmd.deal_id:
            raise HTTPException(400, "deal_id is required.")
        db.commit()
        return WebhookResponse(
            success=True,
            message="Deal status query received. Use GET /deals/{id}/journey.",
            data={"command": cmd.command, "deal_id": cmd.deal_id},
        )

    elif cmd.command in ("get_catalog", "get_pricelist"):
        doc_type = "catalog" if cmd.command == "get_catalog" else "pricelist"
        db.commit()
        return WebhookResponse(
            success=True,
            message=f"Use GET /static-documents/{doc_type}/active to retrieve the file.",
            data={"command": cmd.command},
        )

    else:
        db.commit()
        return WebhookResponse(
            success=False,
            message=f"Unknown command: {cmd.command}",
        )
