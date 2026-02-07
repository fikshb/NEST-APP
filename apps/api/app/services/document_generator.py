"""Document generation service — HTML templates → PDF via WeasyPrint."""
import os
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

    # Build template context
    tenant = deal.tenant
    unit = deal.unit
    context = {
        "deal": deal,
        "tenant": tenant,
        "unit": unit,
        "doc_type": doc_type,
        "version": new_version_no,
        "generated_at": datetime.now(timezone.utc).strftime("%B %d, %Y"),
        "company_name": app_settings.company_legal_name if app_settings else "NEST Serviced Apartment",
        "company_address": app_settings.company_address if app_settings else "",
        "signatory_name": app_settings.signatory_name if app_settings else "",
        "signatory_title": app_settings.signatory_title if app_settings else "",
        "logo_data_uri": _get_logo_base64(app_settings),
    }

    # Render HTML
    template = jinja_env.get_template("document_base.html")
    html_content = template.render(**context)

    # Storage paths
    deal_dir = os.path.join("documents", deal.id)
    html_filename = f"{doc_type}_v{new_version_no}.html"
    pdf_filename = f"{doc_type}_v{new_version_no}.pdf"
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
