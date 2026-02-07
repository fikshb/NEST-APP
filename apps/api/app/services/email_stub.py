"""Email service stub — logs instead of sending real emails."""
import logging

logger = logging.getLogger(__name__)


def send_invoice_request_email(
    finance_email: str,
    deal_code: str,
    tenant_name: str,
    unit_code: str,
    amount: str,
    currency: str,
) -> bool:
    """Stub: log the invoice request email instead of sending."""
    logger.info(
        "[EMAIL STUB] Invoice request sent to %s | Deal: %s | Tenant: %s | Unit: %s | Amount: %s %s",
        finance_email,
        deal_code,
        tenant_name,
        unit_code,
        currency,
        amount,
    )
    return True
