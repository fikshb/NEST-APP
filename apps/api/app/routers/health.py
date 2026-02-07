import smtplib
from email.mime.text import MIMEText

from fastapi import APIRouter

from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    return {"status": "ok", "service": "nestapp-api"}


@router.get("/test-email")
def test_email():
    """Temporary endpoint to debug SMTP connection."""
    info = {
        "smtp_host": settings.smtp_host,
        "smtp_port": settings.smtp_port,
        "smtp_user": settings.smtp_user,
        "finance_email": settings.finance_email,
    }
    if settings.smtp_host == "stub":
        return {"status": "skipped", "reason": "SMTP is stub", **info}

    try:
        msg = MIMEText("This is a test email from NestApp.")
        msg["From"] = settings.smtp_user
        msg["To"] = settings.finance_email
        msg["Subject"] = "[NestApp] Test Email"

        with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=30) as server:
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)

        return {"status": "sent", "to": settings.finance_email, **info}
    except Exception as e:
        return {"status": "error", "error": str(e), **info}
