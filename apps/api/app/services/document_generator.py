"""Document generation service — per-doc-type HTML templates → PDF via WeasyPrint."""
import os
import re
import uuid
from datetime import datetime, timezone

from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

from app.config import settings
from app.models.deal import Deal
from app.models.document import Document, DocumentVersion
from app.models.settings import AppSettings

# Try to import weasyprint; if not available, generate HTML only
try:
    from weasyprint import HTML as WeasyHTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
jinja_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)

# Map doc_type to its dedicated template file
DOC_TYPE_TEMPLATE = {
    "BOOKING_CONFIRMATION": "booking_confirmation.html",
    "LOO_DRAFT": "loo_draft.html",
    "LOO_FINAL": "loo_final.html",
    "LEASE_AGREEMENT": "lease_agreement.html",
    "OFFICIAL_CONFIRMATION": "official_confirmation.html",
    "MOVE_IN_CONFIRMATION": "move_in_confirmation.html",
    "UNIT_HANDOVER": "unit_handover.html",
}

# Human-readable names for file naming
DOC_TYPE_DISPLAY_NAME = {
    "BOOKING_CONFIRMATION": "Booking-Confirmation",
    "LOO_DRAFT": "LOO-Draft",
    "LOO_FINAL": "LOO-Final",
    "LEASE_AGREEMENT": "Lease-Agreement",
    "OFFICIAL_CONFIRMATION": "Official-Confirmation",
    "MOVE_IN_CONFIRMATION": "Move-In-Confirmation",
    "UNIT_HANDOVER": "Unit-Handover",
}


def _sanitize_filename(name: str) -> str:
    """Replace spaces with dashes and remove non-alphanumeric chars (except dash)."""
    name = name.strip().replace(" ", "-")
    return re.sub(r"[^a-zA-Z0-9\-]", "", name)


def _ensure_dir(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)


def _get_settings(db: Session) -> AppSettings | None:
    return db.query(AppSettings).first()


def _get_logo_base64(app_settings: AppSettings | None) -> str:
    """Read logo file and return base64 data URI for embedding in HTML."""
    if not app_settings or not app_settings.logo_path:
        return ""
    logo_full = os.path.join(settings.storage_root, app_settings.logo_path)
    if not os.path.exists(logo_full):
        return ""
    import base64
    with open(logo_full, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    ext = app_settings.logo_path.rsplit(".", 1)[-1].lower()
    mime = {"webp": "image/webp", "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext, "image/png")
    return f"data:{mime};base64,{data}"


def _get_signature_base64(app_settings: AppSettings | None) -> str:
    """Read signature image file and return base64 data URI for embedding in HTML."""
    if not app_settings or not app_settings.signature_image_path:
        return ""
    sig_full = os.path.join(settings.storage_root, app_settings.signature_image_path)
    if not os.path.exists(sig_full):
        return ""
    import base64
    with open(sig_full, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    ext = app_settings.signature_image_path.rsplit(".", 1)[-1].lower()
    mime = {"webp": "image/webp", "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext, "image/png")
    return f"data:{mime};base64,{data}"


def generate_document(
    db: Session,
    deal: Deal,
    doc_type: str,
    channel: str = "WEB",
) -> DocumentVersion:
    """Generate an HTML document and its PDF, store them, and create DB records."""
    app_settings = _get_settings(db)

    # Find or create Document record
    doc = db.query(Document).filter(
        Document.deal_id == deal.id,
        Document.doc_type == doc_type,
    ).first()

    if not doc:
        doc = Document(deal_id=deal.id, doc_type=doc_type, latest_version=0)
        db.add(doc)
        db.flush()

    # Mark old versions as not latest
    for v in doc.versions:
        v.is_latest = False

    new_version_no = doc.latest_version + 1

    # Determine effective price (deal_price if set, otherwise initial_price)
    effective_price = deal.deal_price if deal.deal_price is not None else deal.initial_price

    # Build template context
    tenant = deal.tenant
    unit = deal.unit
    context = {
        "deal": deal,
        "tenant": tenant,
        "unit": unit,
        "doc_type": doc_type,
        "version": new_version_no,
        "effective_price": effective_price,
        "generated_at": datetime.now(timezone.utc).strftime("%B %d, %Y"),
        "company_name": app_settings.company_legal_name if app_settings else "NEST Serviced Apartment",
        "company_address": app_settings.company_address if app_settings else "",
        "signatory_name": app_settings.signatory_name if app_settings else "",
        "signatory_title": app_settings.signatory_title if app_settings else "",
        "logo_data_uri": _get_logo_base64(app_settings),
        "signature_data_uri": _get_signature_base64(app_settings),
        "move_in_date": deal.move_in_date.strftime("%B %d, %Y") if deal.move_in_date else None,
        "move_in_notes": deal.move_in_notes or "",
    }

    # Select template
    template_file = DOC_TYPE_TEMPLATE.get(doc_type, "document_base.html")
    template = jinja_env.get_template(template_file)
    html_content = template.render(**context)

    # Storage paths — format: DocName_TenantName_UnitCode_Date.ext
    deal_dir = os.path.join("documents", deal.id)
    doc_display = DOC_TYPE_DISPLAY_NAME.get(doc_type, doc_type)
    tenant_name = _sanitize_filename(tenant.full_name)
    unit_code = _sanitize_filename(unit.unit_code)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    base_name = f"{doc_display}_{tenant_name}_{unit_code}_{date_str}_v{new_version_no}"
    html_filename = f"{base_name}.html"
    pdf_filename = f"{base_name}.pdf"
    html_rel = os.path.join(deal_dir, html_filename)
    pdf_rel = os.path.join(deal_dir, pdf_filename)

    html_full = os.path.join(settings.storage_root, html_rel)
    pdf_full = os.path.join(settings.storage_root, pdf_rel)

    _ensure_dir(html_full)
    _ensure_dir(pdf_full)

    # Write HTML
    with open(html_full, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Generate PDF
    if WEASYPRINT_AVAILABLE:
        WeasyHTML(string=html_content).write_pdf(pdf_full)
    else:
        # Fallback: copy HTML as placeholder PDF marker
        with open(pdf_full, "w", encoding="utf-8") as f:
            f.write(html_content)

    # Create version record
    version = DocumentVersion(
        document_id=doc.id,
        version_no=new_version_no,
        html_path=html_rel,
        pdf_path=pdf_rel,
        signatory_name=app_settings.signatory_name if app_settings else None,
        signatory_title=app_settings.signatory_title if app_settings else None,
        channel=channel,
        is_latest=True,
    )
    db.add(version)

    doc.latest_version = new_version_no
    db.flush()

    return version
