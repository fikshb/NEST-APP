# NestApp & ClawdBot — Monorepo

**Serviced Apartment Management System** — PRD v8.1

Simple on the surface. Strict underneath.

---

## Architecture

```
├── apps/
│   ├── api/          FastAPI (Python 3.11) + SQLAlchemy + Alembic
│   └── web/          Next.js 14 (App Router) + TypeScript + Tailwind + shadcn/ui
├── packages/
│   └── shared/       Shared constants & types (TS + Python mirror)
├── docs/             PRD, ERD, style guide, architecture mapping
├── storage/          Local file storage (gitignored)
├── initial_asset/    Seed assets: logo, catalog, pricelist
└── docker-compose.yml
```

## Quick Start

### Prerequisites
- Docker & Docker Compose

### Run Everything

```bash
# 1. Clone and enter the project
cd "D:\PROJECT\3. NEST APPS"

# 2. Copy environment file
cp .env.example .env

# 3. Start all services
docker compose up --build
```

This starts:
- **PostgreSQL** on port `5432`
- **API** (FastAPI) on port `8000` — with auto-migration
- **Web** (Next.js) on port `3000`

### Run Migrations (manually)

```bash
docker compose exec api alembic upgrade head
```

### Seed Data

```bash
docker compose exec api python -m app.seed
```

This will:
- Create default Settings (company info, signatory)
- Import `initial_asset/NEST LOGO.webp` as company logo
- Import `initial_asset/NEST UNIT CATALOG.pdf` as active catalog
- Import `initial_asset/NEST PRICELIST.pdf` as active pricelist
- Create 5 sample units (101–105) with pricing
- Create a sample tenant (John Doe)
- Create a sample deal (NEST-00001) in Monthly/In Progress state

### Access

| Service         | URL                          |
|----------------|------------------------------|
| Web UI         | http://localhost:3000         |
| API Docs       | http://localhost:8000/docs    |
| API Health     | http://localhost:8000/health  |

---

## Environment Variables

See `.env.example` for all variables. Key ones:

| Variable                 | Description                              |
|--------------------------|------------------------------------------|
| `DATABASE_URL`           | PostgreSQL connection string             |
| `STORAGE_ROOT`           | Local file storage root path             |
| `OPENCLAW_SERVICE_TOKEN` | Bot service token for webhook auth       |
| `FINANCE_EMAIL`          | Finance department email (stub)          |
| `NEXT_PUBLIC_API_URL`    | API URL for frontend                     |

---

## API Endpoints

Full OpenAPI docs at `http://localhost:8000/docs`.

### Core Endpoints

| Method | Path                                         | Description                        |
|--------|----------------------------------------------|------------------------------------|
| GET    | `/health`                                    | Health check                       |
| GET    | `/dashboard`                                 | Dashboard summary + chart data     |
| CRUD   | `/tenants`                                   | Tenant management                  |
| CRUD   | `/units`                                     | Unit management                    |
| GET/POST/PATCH | `/deals`                             | Deal management (no hard delete)   |
| GET    | `/deals/{id}/journey`                        | Journey status with step checklist |
| POST   | `/deals/{id}/actions/generate-document`      | Generate next document             |
| POST   | `/deals/{id}/actions/request-invoice`        | Request invoice from finance       |
| POST   | `/deals/{id}/actions/upload-invoice`         | Upload invoice (multipart)         |
| POST   | `/deals/{id}/actions/close`                  | Close completed deal               |
| POST   | `/deals/{id}/actions/cancel`                 | Cancel deal (reason required)      |
| POST   | `/deals/{id}/actions/emergency-override`     | Emergency override (web only)      |
| GET    | `/documents`                                 | List deal documents                |
| GET    | `/documents/{id}/latest/pdf`                 | Download latest PDF                |
| GET/POST | `/static-documents`                        | Catalog & pricelist management     |
| GET    | `/static-documents/{type}/active`            | Download active catalog/pricelist  |
| GET/PUT | `/settings`                                 | App settings                       |
| POST   | `/settings/logo`                             | Upload company logo                |
| POST   | `/settings/signature`                        | Upload signature image             |
| GET    | `/audit-logs`                                | Query audit logs                   |
| GET    | `/audit-logs/export`                         | Export audit logs as CSV           |
| POST   | `/integrations/openclaw/webhook`             | Bot webhook endpoint               |

---

## File Storage & Versioning

All files are stored under `./storage/` (mounted as `/app/storage` in Docker):

```
storage/
├── settings/           Company logo, signature images
├── static_documents/
│   ├── catalog/        catalog_v1.pdf, catalog_v2.pdf, ...
│   └── pricelist/      pricelist_v1.pdf, ...
├── documents/
│   └── {deal_id}/      BOOKING_CONFIRMATION_v1.html, .pdf, ...
└── finance/
    └── {deal_id}/      invoice_xxxxx.pdf
```

**Versioning rules:**
- Documents are immutable — revisions create a new version
- Old versions are read-only, new version is marked `is_latest`
- Static documents have one `active` version per type
- Files are never deleted

---

## Simulating Bot Webhook Calls

The bot webhook at `/integrations/openclaw/webhook` requires a Bearer token:

```bash
# Example: Send a bot command
curl -X POST http://localhost:8000/integrations/openclaw/webhook \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dev-bot-token-change-in-prod" \
  -d '{
    "command": "generate_document",
    "deal_id": "<deal-uuid>"
  }'
```

Supported commands: `create_deal`, `generate_document`, `request_invoice`, `get_deal_status`, `get_catalog`, `get_pricelist`

All webhook calls are logged with:
- Actor: ADMIN
- Channel: WHATSAPP
- Executor: CLAWDBOT

---

## Journey State Machine

### Daily Stay (7 steps)
1. Select Unit → 2. Generate Booking Confirmation → 3. Generate Official Confirmation →
4. Request Invoice → 5. Upload Invoice → 6. Generate Handover Certificate → 7. Deal Closed

### Monthly / 6 / 12 Months (10 steps)
1. Select Unit → 2. Generate LOO Draft → 3. Finalize LOO → 4. Generate Lease Agreement →
5. Generate Official Confirmation → 6. Request Invoice → 7. Upload Invoice →
8. Generate Move-in Confirmation → 9. Generate Handover Certificate → 10. Deal Closed

**Rules:**
- Steps unlock sequentially
- No document → no progress
- Bot cannot bypass journey rules
- Emergency override is web-only, admin-only, fully auditable

---

## PDF Generation

Documents are generated using **WeasyPrint** (HTML → PDF):
- Templates in `apps/api/app/templates/`
- Each document type has a formal business letter layout
- NEST logo and company signature are auto-embedded
- HTML preview and PDF download are separate endpoints

If WeasyPrint is not available (missing system dependencies), the system falls back to HTML-only output.

---

## Tech Stack

| Layer     | Technology                                        |
|-----------|--------------------------------------------------|
| Frontend  | Next.js 14 (App Router), TypeScript, Tailwind CSS |
| UI        | shadcn/ui, Recharts, Lucide Icons                |
| Backend   | FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2   |
| Database  | PostgreSQL 16                                     |
| PDF       | WeasyPrint                                        |
| Storage   | Local filesystem (Phase 1)                        |
| Container | Docker Compose                                    |
