from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os

from app.config import settings
from app.database import engine, Base
from app.dependencies.auth import get_current_user
from app.routers import health, tenants, units, deals, documents, static_documents, app_settings, audit_logs, dashboard, webhook, auth

# Import all models so Base.metadata knows about them
from app.models import *  # noqa: F401,F403

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup (idempotent — skips existing tables)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
    yield


app = FastAPI(
    title="NestApp API",
    description="Serviced Apartment Management System — PRD v8.1",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount storage for serving files
storage_path = settings.storage_root
if os.path.isdir(storage_path):
    app.mount("/files", StaticFiles(directory=storage_path), name="files")

# Public routers (no auth required)
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(webhook.router)

# Document routers — use per-endpoint auth (supports token query param for preview/download)
app.include_router(documents.router)
app.include_router(static_documents.router)

# Protected routers (auth required)
protected = [dashboard, tenants, units, deals, app_settings, audit_logs]
for mod in protected:
    app.include_router(mod.router, dependencies=[Depends(get_current_user)])
