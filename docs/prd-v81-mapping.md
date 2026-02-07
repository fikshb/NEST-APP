# PRD v8.1 → Implementation Mapping

This document maps each PRD section to its implementation location.

## Section Mapping

| PRD Section | Impl Location | Status |
|---|---|---|
| **2. User & Actors** | Single admin, no RBAC. Bot acts via webhook. | Done |
| **3. Core Design Principles** | Enforced across journey service, audit logging, document immutability | Done |
| **4.1 Dashboard** | `apps/web/src/app/page.tsx` + `apps/api/app/routers/dashboard.py` | Done |
| **4.2 Side Menu** | `apps/web/src/components/sidebar.tsx` | Done |
| **5. Core Object: Deal** | `apps/api/app/models/deal.py` | Done |
| **6. Deal Journeys** | `apps/api/app/services/journey.py` — daily (7 steps) & monthly (10 steps) | Done |
| **7. Deal Detail Page** | `apps/web/src/app/deals/[id]/page.tsx` — journey checklist + single CTA | Done |
| **8.1 System-Generated Docs** | `apps/api/app/services/document_generator.py` + WeasyPrint templates | Done |
| **8.2 Document Rules** | Immutable, versioned, never deleted. Enforced in models + routers. | Done |
| **9. Static Documents** | `apps/api/app/routers/static_documents.py` + `apps/web/src/app/documents/page.tsx` | Done |
| **10. Tenants Module** | `apps/api/app/routers/tenants.py` + `apps/web/src/app/tenants/page.tsx` | Done |
| **11. Units Module** | `apps/api/app/routers/units.py` + `apps/web/src/app/units/page.tsx` | Done |
| **12. Finance Handling** | Request invoice action + upload invoice action in `deals.py` router | Done |
| **13. E-Signature** | Signature image upload in settings; auto-embedded in generated docs | Done |
| **14. Deal Cancellation** | `POST /deals/{id}/actions/cancel` — reason mandatory, unit released, logged | Done |
| **14. Emergency Override** | `POST /deals/{id}/actions/emergency-override` — web only, reason mandatory | Done |
| **15. ClawdBot Integration** | `apps/api/app/routers/webhook.py` — token auth, audit logging, command stubs | Done |
| **16. Settings** | `apps/api/app/routers/app_settings.py` + `apps/web/src/app/settings/page.tsx` | Done |
| **17. Audit & Compliance** | `apps/api/app/services/audit.py` + `apps/api/app/routers/audit_logs.py` + CSV export | Done |
| **18. Error Communication** | Plain language messages throughout — no error codes shown to admin | Done |
| **19. Performance** | Lightweight aggregation queries for dashboard, read-only charts | Done |

## Data Model

See `docs/Entity Relationship Diagram.md` for the full ERD.

Implementation uses simplified schema:
- `AppSettings` single table instead of separate company/finance/bot settings tables
- `Unit` pricing inline instead of separate pricing table
- Journey state tracked on Deal (`current_step`) instead of separate state table

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
