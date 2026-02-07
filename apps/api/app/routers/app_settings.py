import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.settings import AppSettings
from app.schemas.settings import SettingsUpdate, SettingsResponse
from app.services.audit import log_action
from app.config import settings as app_config

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    s = db.query(AppSettings).first()
    if not s:
        raise HTTPException(404, "Settings not initialized. Please run the seed command.")
    return s


@router.put("", response_model=SettingsResponse)
def update_settings(data: SettingsUpdate, db: Session = Depends(get_db)):
    s = db.query(AppSettings).first()
    if not s:
        raise HTTPException(404, "Settings not initialized.")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(s, field, value)
    log_action(db, action="UPDATE_SETTINGS", summary="Updated company settings")
    db.commit()
    db.refresh(s)
    return s


@router.post("/logo", response_model=SettingsResponse)
def upload_logo(file: UploadFile = File(...), db: Session = Depends(get_db)):
    s = db.query(AppSettings).first()
    if not s:
        raise HTTPException(404, "Settings not initialized.")

    file_dir = os.path.join("settings")
    full_dir = os.path.join(app_config.storage_root, file_dir)
    os.makedirs(full_dir, exist_ok=True)

    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "png"
    stored_name = f"logo_{uuid.uuid4().hex[:8]}.{ext}"
    file_path = os.path.join(file_dir, stored_name)
    full_path = os.path.join(app_config.storage_root, file_path)

    with open(full_path, "wb") as f:
        f.write(file.file.read())

    s.logo_path = file_path
    log_action(db, action="UPDATE_SETTINGS", summary="Updated company logo")
    db.commit()
    db.refresh(s)
    return s


@router.post("/signature", response_model=SettingsResponse)
def upload_signature(file: UploadFile = File(...), db: Session = Depends(get_db)):
    s = db.query(AppSettings).first()
    if not s:
        raise HTTPException(404, "Settings not initialized.")

    file_dir = os.path.join("settings")
    full_dir = os.path.join(app_config.storage_root, file_dir)
    os.makedirs(full_dir, exist_ok=True)

    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "png"
    stored_name = f"signature_{uuid.uuid4().hex[:8]}.{ext}"
    file_path = os.path.join(file_dir, stored_name)
    full_path = os.path.join(app_config.storage_root, file_path)

    with open(full_path, "wb") as f:
        f.write(file.file.read())

    s.signature_image_path = file_path
    log_action(db, action="UPDATE_SETTINGS", summary="Updated signature image")
    db.commit()
    db.refresh(s)
    return s
