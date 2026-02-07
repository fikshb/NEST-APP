from pydantic import BaseModel
from datetime import datetime


class DocumentVersionResponse(BaseModel):
    id: str
    version_no: int
    html_path: str
    pdf_path: str
    channel: str
    is_latest: bool
    generated_at: datetime

    model_config = {"from_attributes": True}


class DocumentResponse(BaseModel):
    id: str
    deal_id: str
    doc_type: str
    latest_version: int
    versions: list[DocumentVersionResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class StaticDocumentVersionResponse(BaseModel):
    id: str
    version_no: int
    file_name: str
    file_path: str
    notes: str | None
    uploaded_at: datetime
    is_active: bool

    model_config = {"from_attributes": True}


class StaticDocumentResponse(BaseModel):
    id: str
    doc_type: str
    active_version_id: str | None
    versions: list[StaticDocumentVersionResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}
