"""Email service — sends emails via Resend HTTP API or falls back to logging."""
import base64
import json
import logging
import os
import urllib.request
from datetime import datetime, timezone

from app.config import settings

logger = logging.getLogger(__name__)

RESEND_API_URL = "https://api.resend.com/emails"


def _build_invoice_html(
    deal_code: str,
    tenant_name: str,
    unit_code: str,
    amount: str,
    currency: str,
) -> str:
    """Build HTML email body for invoice request."""
    now = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    return f"""\
<html>
<body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto;">
  <div style="background: #1a1a2e; color: #fff; padding: 20px; text-align: center;">
    <h2 style="margin: 0;">NEST Serviced Apartment</h2>
    <p style="margin: 5px 0 0; font-size: 14px;">Invoice Request</p>
  </div>
  <div style="padding: 24px; border: 1px solid #e0e0e0; border-top: none;">
    <p>Dear Finance Team,</p>
    <p>A new invoice has been requested. Please find the details below:</p>
    <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
      <tr style="border-bottom: 1px solid #e0e0e0;">
        <td style="padding: 10px; font-weight: bold; width: 40%;">Deal Code</td>
        <td style="padding: 10px;">{deal_code}</td>
      </tr>
      <tr style="border-bottom: 1px solid #e0e0e0;">
        <td style="padding: 10px; font-weight: bold;">Tenant</td>
        <td style="padding: 10px;">{tenant_name}</td>
      </tr>
      <tr style="border-bottom: 1px solid #e0e0e0;">
        <td style="padding: 10px; font-weight: bold;">Unit</td>
        <td style="padding: 10px;">{unit_code}</td>
      </tr>
      <tr style="border-bottom: 1px solid #e0e0e0;">
        <td style="padding: 10px; font-weight: bold;">Amount</td>
        <td style="padding: 10px; font-size: 18px; font-weight: bold;">{currency} {amount}</td>
      </tr>
    </table>
    <p>Please process this invoice at your earliest convenience.</p>
    <p style="color: #888; font-size: 12px;">Requested on {now}</p>
  </div>
  <div style="background: #f5f5f5; padding: 12px; text-align: center; font-size: 12px; color: #888;">
    NestApp — Serviced Apartment Management System
  </div>
</body>
</html>"""


def send_invoice_request_email(
    finance_email: str,
    deal_code: str,
    tenant_name: str,
    unit_code: str,
    amount: str,
    currency: str,
    pdf_path: str | None = None,
) -> bool:
    """Send invoice request email via Resend. Falls back to logging if API key is stub."""
    # Stub mode — just log
    if settings.resend_api_key == "stub":
        logger.info(
            "[EMAIL STUB] Invoice request → %s | Deal: %s | Tenant: %s | Unit: %s | Amount: %s %s",
            finance_email, deal_code, tenant_name, unit_code, currency, amount,
        )
        return True

    try:
        html_body = _build_invoice_html(deal_code, tenant_name, unit_code, amount, currency)

        payload = {
            "from": settings.email_from,
            "to": [finance_email],
            "subject": f"[NestApp] Invoice Request — {deal_code}",
            "html": html_body,
        }

        # Attach PDF if available
        if pdf_path and os.path.isfile(pdf_path):
            with open(pdf_path, "rb") as f:
                pdf_b64 = base64.b64encode(f.read()).decode("utf-8")
            payload["attachments"] = [{
                "filename": os.path.basename(pdf_path),
                "content": pdf_b64,
            }]

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            RESEND_API_URL,
            data=data,
            headers={
                "Authorization": f"Bearer {settings.resend_api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        logger.info("[EMAIL] Invoice request sent to %s for deal %s (id: %s)", finance_email, deal_code, result.get("id"))
        return True

    except Exception as e:
        logger.error("[EMAIL] Failed to send invoice request for deal %s: %s", deal_code, e)
        return False
