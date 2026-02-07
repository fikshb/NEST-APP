# PRD v8.1 → Implementation Mapping

This document maps each PRD section to its implementation location.

## Section Mapping

| PRD Section | Impl Location | Status |
|---|---|---|
| **2. User & Actors** | Single admin via env vars (`ADMIN_USER`, `ADMIN_PASSWORD`). No RBAC. Bot acts via webhook. | Done |
| **3. Core Design Principles** | Enforced across journey service, audit logging, document immutability | Done |
| **4.1 Dashboard** | `apps/web/src/app/page.tsx` + `apps/api/app/routers/dashboard.py` | Done |
| **4.2 Side Menu** | `apps/web/src/components/sidebar.tsx` (with logout button) | Done |
| **5. Core Object: Deal** | `apps/api/app/models/deal.py` | Done |
| **6.1 Daily Journey** | `apps/api/app/services/journey.py` — **5 steps** (Select Unit → Booking Confirmation → Request Invoice → Upload Invoice → Deal Closed) | Done |
| **6.2 Monthly/6M/12M Journey** | `apps/api/app/services/journey.py` — 10 steps (includes LOO Draft/Final, Lease, Official Confirmation, Move-in, Handover) | Done |
| **7. Deal Detail Page** | `apps/web/src/app/deals/[id]/page.tsx` — journey checklist + single CTA + price input + move-in input | Done |
| **8.1 System-Generated Docs** | `apps/api/app/services/document_generator.py` + WeasyPrint templates in `apps/api/app/templates/` | Done |
| **8.2 Document Rules** | Immutable, versioned, never deleted. Enforced in models + routers. | Done |
| **9. Static Documents** | `apps/api/app/routers/static_documents.py` + `apps/web/src/app/documents/page.tsx` | Done |
| **10. Tenants Module** | `apps/api/app/routers/tenants.py` + `apps/web/src/app/tenants/page.tsx` | Done |
| **11. Units Module** | `apps/api/app/routers/units.py` + `apps/web/src/app/units/page.tsx` | Done |
| **12. Finance Handling** | Request invoice action + upload invoice action in `deals.py` router | Done |
| **13. E-Signature** | Signature image upload in settings; auto-embedded as base64 in generated docs | Done |
| **14. Deal Cancellation** | `POST /deals/{id}/actions/cancel` — reason mandatory, unit released, logged | Done |
| **14. Emergency Override** | `POST /deals/{id}/actions/emergency-override` — web only, reason mandatory | Done |
| **15. ClawdBot Integration** | `apps/api/app/routers/webhook.py` — token auth, audit logging, command stubs | Done |
| **16. Settings** | `apps/api/app/routers/app_settings.py` + `apps/web/src/app/settings/page.tsx` | Done |
| **17. Audit & Compliance** | `apps/api/app/services/audit.py` + `apps/api/app/routers/audit_logs.py` + CSV export | Done |
| **18. Error Communication** | Plain language messages throughout — no error codes shown to admin | Done |
| **19. Performance** | Lightweight aggregation queries for dashboard, read-only charts | Done |
| **21. Authentication** | `apps/api/app/routers/auth.py` + `apps/api/app/dependencies/auth.py` + `apps/web/src/app/login/page.tsx` + `apps/web/src/components/auth-guard.tsx` | Done |

## Authentication System

| Component | File | Description |
|---|---|---|
| Auth config | `apps/api/app/config.py` | `admin_user`, `admin_password` env vars |
| Auth router | `apps/api/app/routers/auth.py` | `POST /auth/login`, `GET /auth/me` |
| Auth dependency | `apps/api/app/dependencies/auth.py` | `get_current_user` (Bearer header), `get_current_user_or_token` (header + query param) |
| Route protection | `apps/api/app/main.py` | All routers except health, auth, webhook require auth |
| Login page | `apps/web/src/app/login/page.tsx` | Username/password form |
| Auth guard | `apps/web/src/components/auth-guard.tsx` | Wraps all pages, redirects to /login if unauthenticated |
| Token helpers | `apps/web/src/lib/auth.ts` | `getToken()`, `setToken()`, `removeToken()`, `isAuthenticated()` |
| API client | `apps/web/src/lib/api.ts` | Auto-attaches Bearer token, handles 401 redirect |
| Logout | `apps/web/src/components/sidebar.tsx` | Logout button clears token, redirects to /login |

## Data Model

See `docs/Entity Relationship Diagram.md` for the full ERD.

Implementation uses simplified schema:
- No `ADMINS` table — single admin via env vars with JWT auth
- `AppSettings` single table instead of separate company/finance/bot settings tables
- `Unit` pricing inline instead of separate pricing table
- Journey state tracked on Deal (`current_step`) instead of separate state table

## Price Negotiation

| Step | Available At | Description |
|---|---|---|
| `FINALIZE_LOO` | Monthly, 6M, 12M deals | Set negotiated price before generating LOO Final |
| `GENERATE_BOOKING_CONFIRMATION` | Daily deals | Set negotiated price before generating Booking Confirmation |

If no negotiated price is set, `initial_price` (from unit pricing) is used as `deal_price` automatically at document generation.

## Document Filename Format

Documents are saved with descriptive filenames:
```
{DocName}_{TenantName}_{UnitCode}_{Date}_v{Version}.{ext}
```
Example: `Booking-Confirmation_John-Doe_101_2026-02-07_v1.pdf`

## Document Preview Auth

Document preview and PDF download endpoints support two auth methods:
1. **Bearer header** — standard API auth (used by API calls)
2. **Query param** — `?token=<jwt>` (used when opening in new browser tab)

This is implemented via `get_current_user_or_token` dependency on:
- `GET /documents/{id}/versions/{vid}/preview`
- `GET /documents/{id}/versions/{vid}/pdf`
- `GET /documents/{id}/latest/pdf`
- `GET /static-documents/{type}/active`

## Shared Constants

Single source of truth at `packages/shared/`:
- `constants.ts` — TypeScript (imported by web app)
- `constants.py` — Python mirror (imported by API)
- `types.ts` — API contract types

## Non-Goals (Not Implemented)

Per PRD:
- No RBAC / multiple users
- No external tenant portal
- No real WhatsApp integration
- No real payment gateways
- No advanced analytics
- No real email provider (stub only)
