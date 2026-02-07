"""
Seed script — run after migrations to populate initial data.

Usage: python -m app.seed
"""
import os
import shutil
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models.settings import AppSettings
from app.models.tenant import Tenant
from app.models.unit import Unit
from app.models.deal import Deal
from app.models.static_document import StaticDocument, StaticDocumentVersion
from app.config import settings


def _copy_initial_asset(src_filename: str, dest_rel_path: str) -> str:
    """Copy a file from initial_asset/ to storage/ and return relative path."""
    src = os.path.join(settings.initial_asset_path, src_filename)
    dest = os.path.join(settings.storage_root, dest_rel_path)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.exists(src):
        shutil.copy2(src, dest)
        print(f"  Copied: {src_filename} → {dest_rel_path}")
    else:
        print(f"  WARNING: Source not found: {src}")
    return dest_rel_path


def seed():
    os.makedirs(settings.storage_root, exist_ok=True)

    db: Session = SessionLocal()
    try:
        # ── 1. Settings ──
        existing = db.query(AppSettings).first()
        if existing:
            print("Settings already exist, skipping settings seed.")
        else:
            print("Creating default settings...")
            logo_path = _copy_initial_asset("NEST LOGO.webp", "settings/logo.webp")
            s = AppSettings(
                company_legal_name="NEST Serviced Apartment",
                company_address="Jakarta, Indonesia",
                logo_path=logo_path,
                signatory_name="Management",
                signatory_title="General Manager",
                finance_email="finance@example.com",
                bot_whatsapp_number="+62800000000",
            )
            db.add(s)
            db.flush()
            print(f"  Settings created (id={s.id})")

        # ── 2. Static Documents (Catalog + Pricelist) ──
        for doc_type, filename in [("CATALOG", "NEST UNIT CATALOG.pdf"), ("PRICELIST", "NEST PRICELIST.pdf")]:
            existing_sd = db.query(StaticDocument).filter(StaticDocument.doc_type == doc_type).first()
            if existing_sd:
                print(f"{doc_type} already exists, skipping.")
                continue

            print(f"Seeding {doc_type}...")
            dest_path = _copy_initial_asset(
                filename,
                f"static_documents/{doc_type.lower()}/{doc_type.lower()}_v1.pdf",
            )
            sd = StaticDocument(doc_type=doc_type)
            db.add(sd)
            db.flush()

            ver = StaticDocumentVersion(
                static_document_id=sd.id,
                version_no=1,
                file_name=filename,
                file_path=dest_path,
                notes="Initial seed from initial_asset/",
                is_active=True,
            )
            db.add(ver)
            db.flush()
            sd.active_version_id = ver.id
            print(f"  {doc_type} v1 created (id={sd.id})")

        # ── 3. Sample Units ──
        unit_ids = []
        existing_units = db.query(Unit).count()
        if existing_units > 0:
            print(f"{existing_units} units already exist, skipping unit seed.")
            unit_ids = [u.id for u in db.query(Unit).limit(5).all()]
        else:
            print("Creating sample units (101-105)...")
            for code in ["101", "102", "103", "104", "105"]:
                u = Unit(
                    unit_code=code,
                    unit_type="Standard" if code in ("101", "102", "103") else "Deluxe",
                    daily_price=Decimal("500000"),
                    monthly_price=Decimal("8000000"),
                    six_month_price=Decimal("42000000"),
                    twelve_month_price=Decimal("78000000"),
                    currency="IDR",
                )
                db.add(u)
                db.flush()
                unit_ids.append(u.id)
                print(f"  Unit {code} created (id={u.id})")

        # ── 4. Sample Tenant ──
        existing_tenants = db.query(Tenant).count()
        if existing_tenants > 0:
            print("Tenants already exist, skipping tenant seed.")
            tenant = db.query(Tenant).first()
        else:
            print("Creating sample tenant...")
            tenant = Tenant(
                full_name="John Doe",
                phone="+6281234567890",
                email="john.doe@example.com",
                company_name="Acme Corp",
                notes="Sample tenant for development",
            )
            db.add(tenant)
            db.flush()
            print(f"  Tenant created: {tenant.full_name} (id={tenant.id})")

        # ── 5. Sample Deal (Draft) ──
        existing_deals = db.query(Deal).count()
        if existing_deals > 0:
            print("Deals already exist, skipping deal seed.")
        else:
            print("Creating sample deal...")
            deal = Deal(
                deal_code="NEST-00001",
                tenant_id=tenant.id,
                unit_id=unit_ids[0] if unit_ids else None,
                term_type="MONTHLY",
                start_date=date.today(),
                initial_price=Decimal("8000000"),
                currency="IDR",
                status="IN_PROGRESS",
                current_step="GENERATE_LOO_DRAFT",
            )
            db.add(deal)
            db.flush()

            # Reserve the unit
            if unit_ids:
                first_unit = db.query(Unit).filter(Unit.id == unit_ids[0]).first()
                if first_unit:
                    first_unit.status = "RESERVED"

            print(f"  Deal created: {deal.deal_code} (id={deal.id})")

        db.commit()
        print("\nSeed completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
