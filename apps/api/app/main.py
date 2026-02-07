from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings
from app.routers import health, tenants, units, deals, documents, static_documents, app_settings, audit_logs, dashboard, webhook

app = FastAPI(
    title="NestApp API",
    description="Serviced Apartment Management System — PRD v8.1",
    version="1.0.0",
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

# Register routers
app.include_router(health.router)
app.include_router(dashboard.router)
app.include_router(tenants.router)
app.include_router(units.router)
app.include_router(deals.router)
app.include_router(documents.router)
app.include_router(static_documents.router)
app.include_router(app_settings.router)
app.include_router(audit_logs.router)
app.include_router(webhook.router)
