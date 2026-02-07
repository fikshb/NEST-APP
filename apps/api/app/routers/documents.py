import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.document import Document, DocumentVersion
from app.schemas.document import DocumentResponse, DocumentVersionResponse
from app.config import settings
from app.dependencies.auth import get_current_user, get_current_user_or_token

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("", response_model=list[DocumentResponse])
def list_documents(deal_id: str | None = None, db: Session = Depends(get_db), _user: str = Depends(get_current_user)):
    q = db.query(Document).options(joinedload(Document.versions))
    if deal_id:
        q = q.filter(Document.deal_id == deal_id)
    return q.order_by(Document.created_at.desc()).all()


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str, db: Session = Depends(get_db), _user: str = Depends(get_current_user)):
    doc = db.query(Document).options(joinedload(Document.versions)).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found.")
    return doc


@router.get("/{document_id}/versions/{version_id}/preview")
def preview_document(document_id: str, version_id: str, db: Session = Depends(get_db), _user: str = Depends(get_current_user_or_token)):
    version = db.query(DocumentVersion).filter(
        DocumentVersion.id == version_id,
        DocumentVersion.document_id == document_id,
    ).first()
    if not version:
        raise HTTPException(404, "Document version not found.")

    full_path = os.path.join(settings.storage_root, version.html_path)
    if not os.path.exists(full_path):
        raise HTTPException(404, "HTML file not found on disk.")
    return FileResponse(full_path, media_type="text/html")


@router.get("/{document_id}/versions/{version_id}/pdf")
def download_document_pdf(document_id: str, version_id: str, db: Session = Depends(get_db), _user: str = Depends(get_current_user_or_token)):
    version = db.query(DocumentVersion).filter(
        DocumentVersion.id == version_id,
        DocumentVersion.document_id == document_id,
    ).first()
    if not version:
        raise HTTPException(404, "Document version not found.")

    full_path = os.path.join(settings.storage_root, version.pdf_path)
    if not os.path.exists(full_path):
        raise HTTPException(404, "PDF file not found on disk.")
    return FileResponse(full_path, media_type="application/pdf", filename=os.path.basename(version.pdf_path))


@router.get("/{document_id}/latest/pdf")
def download_latest_pdf(document_id: str, db: Session = Depends(get_db), _user: str = Depends(get_current_user_or_token)):
    version = db.query(DocumentVersion).filter(
        DocumentVersion.document_id == document_id,
        DocumentVersion.is_latest == True,
    ).first()
    if not version:
        raise HTTPException(404, "No version found for this document.")

    full_path = os.path.join(settings.storage_root, version.pdf_path)
    if not os.path.exists(full_path):
        raise HTTPException(404, "PDF file not found on disk.")
    return FileResponse(full_path, media_type="application/pdf", filename=os.path.basename(version.pdf_path))
