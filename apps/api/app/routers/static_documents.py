import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.static_document import StaticDocument, StaticDocumentVersion
from app.schemas.document import StaticDocumentResponse
from app.services.audit import log_action
from app.config import settings
from app.dependencies.auth import get_current_user, get_current_user_or_token

router = APIRouter(prefix="/static-documents", tags=["Static Documents"])


@router.get("", response_model=list[StaticDocumentResponse])
def list_static_documents(db: Session = Depends(get_db), _user: str = Depends(get_current_user)):
    return db.query(StaticDocument).options(joinedload(StaticDocument.versions)).all()


@router.get("/{doc_type}/active")
def get_active_static_document(doc_type: str, db: Session = Depends(get_db), _user: str = Depends(get_current_user_or_token)):
    """Get the active version of a static document (CATALOG or PRICELIST)."""
    doc_type = doc_type.upper()
    sdoc = db.query(StaticDocument).filter(StaticDocument.doc_type == doc_type).first()
    if not sdoc or not sdoc.active_version_id:
        raise HTTPException(404, f"No active {doc_type.lower()} found.")

    version = db.query(StaticDocumentVersion).filter(
        StaticDocumentVersion.id == sdoc.active_version_id,
    ).first()
    if not version:
        raise HTTPException(404, "Active version record not found.")

    full_path = os.path.join(settings.storage_root, version.file_path)
    if not os.path.exists(full_path):
        raise HTTPException(404, "File not found on disk.")
    return FileResponse(full_path, media_type="application/pdf", filename=version.file_name)


@router.post("/{doc_type}/upload", response_model=StaticDocumentResponse)
def upload_static_document(
    doc_type: str,
    file: UploadFile = File(...),
    notes: str = Form(""),
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    doc_type = doc_type.upper()
    if doc_type not in ("CATALOG", "PRICELIST"):
        raise HTTPException(400, "Document type must be CATALOG or PRICELIST.")

    # Find or create the static document record
    sdoc = db.query(StaticDocument).filter(StaticDocument.doc_type == doc_type).first()
    if not sdoc:
        sdoc = StaticDocument(doc_type=doc_type)
        db.add(sdoc)
        db.flush()

    # Determine version number
    max_ver = 0
    for v in sdoc.versions:
        if v.version_no > max_ver:
            max_ver = v.version_no
    new_ver = max_ver + 1

    # Save file
    file_dir = os.path.join("static_documents", doc_type.lower())
    full_dir = os.path.join(settings.storage_root, file_dir)
    os.makedirs(full_dir, exist_ok=True)

    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "pdf"
    stored_name = f"{doc_type.lower()}_v{new_ver}.{ext}"
    file_path = os.path.join(file_dir, stored_name)
    full_path = os.path.join(settings.storage_root, file_path)

    with open(full_path, "wb") as f:
        content = file.file.read()
        f.write(content)

    # Deactivate old versions
    for v in sdoc.versions:
        v.is_active = False

    # Create new version
    version = StaticDocumentVersion(
        static_document_id=sdoc.id,
        version_no=new_ver,
        file_name=file.filename,
        file_path=file_path,
        notes=notes,
        is_active=True,
    )
    db.add(version)
    db.flush()

    sdoc.active_version_id = version.id

    log_action(
        db,
        action="UPLOAD_STATIC_DOCUMENT",
        summary=f"Uploaded {doc_type} v{new_ver}: {file.filename}",
    )
    db.commit()
    db.refresh(sdoc)

    return db.query(StaticDocument).options(joinedload(StaticDocument.versions)).filter(StaticDocument.id == sdoc.id).first()


@router.post("/{doc_type}/versions/{version_id}/activate", response_model=StaticDocumentResponse)
def activate_static_document_version(doc_type: str, version_id: str, db: Session = Depends(get_db), _user: str = Depends(get_current_user)):
    doc_type = doc_type.upper()
    sdoc = db.query(StaticDocument).filter(StaticDocument.doc_type == doc_type).first()
    if not sdoc:
        raise HTTPException(404, f"No {doc_type.lower()} record found.")

    version = db.query(StaticDocumentVersion).filter(
        StaticDocumentVersion.id == version_id,
        StaticDocumentVersion.static_document_id == sdoc.id,
    ).first()
    if not version:
        raise HTTPException(404, "Version not found.")

    for v in sdoc.versions:
        v.is_active = False
    version.is_active = True
    sdoc.active_version_id = version.id

    log_action(
        db,
        action="ACTIVATE_STATIC_DOCUMENT",
        summary=f"Activated {doc_type} v{version.version_no}",
    )
    db.commit()
    db.refresh(sdoc)
    return db.query(StaticDocument).options(joinedload(StaticDocument.versions)).filter(StaticDocument.id == sdoc.id).first()
