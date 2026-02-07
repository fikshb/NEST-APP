import json
import urllib.request

from fastapi import APIRouter

from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    return {"status": "ok", "service": "nestapp-api"}


@router.get("/test-email")
def test_email():
    """Temporary endpoint to debug email sending."""
    info = {
        "resend_api_key": settings.resend_api_key[:10] + "..." if len(settings.resend_api_key) > 10 else settings.resend_api_key,
        "email_from": settings.email_from,
        "finance_email": settings.finance_email,
    }
    if settings.resend_api_key == "stub":
        return {"status": "skipped", "reason": "Resend API key is stub", **info}

    try:
        payload = {
            "from": settings.email_from,
            "to": [settings.finance_email],
            "subject": "[NestApp] Test Email",
            "html": "<p>This is a test email from NestApp.</p>",
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            "https://api.resend.com/emails",
            data=data,
            headers={
                "Authorization": f"Bearer {settings.resend_api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        return {"status": "sent", "resend_id": result.get("id"), **info}
    except Exception as e:
        return {"status": "error", "error": str(e), **info}
