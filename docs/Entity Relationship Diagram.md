# Entity Relationship Diagram — NestApp (As Implemented)

> This ERD reflects the **actual database schema** as implemented. The original PRD proposed
> separate tables (ADMINS, UNIT_PRICING, COMPANY_SETTINGS, FINANCE_SETTINGS, BOT_SETTINGS,
> SIGNATURE_ASSETS); the implementation uses a simplified schema noted below.

```mermaid
erDiagram
  TENANTS ||--o{ DEALS : participates_in
  UNITS ||--o{ DEALS : booked_for

  DEALS ||--o{ DOCUMENTS : has
  DOCUMENTS ||--o{ DOCUMENT_VERSIONS : versions

  DEALS ||--o{ FINANCE_ATTACHMENTS : has
  DEALS ||--o{ AUDIT_LOGS : has

  STATIC_DOCUMENTS ||--o{ STATIC_DOCUMENT_VERSIONS : versions

  TENANTS {
    uuid id PK
    string full_name
    string phone
    string email
    string company_name "nullable"
    text notes "nullable"
    boolean is_archived "default false"
    datetime created_at
    datetime updated_at
  }

  UNITS {
    uuid id PK
    string unit_code "unique"
    string unit_type "default Standard"
    string status "AVAILABLE|RESERVED|OCCUPIED"
    text notes "nullable"
    decimal daily_price "nullable"
    decimal monthly_price "nullable"
    decimal six_month_price "nullable"
    decimal twelve_month_price "nullable"
    string currency "default IDR"
    datetime created_at
    datetime updated_at
  }

  DEALS {
    uuid id PK
    string deal_code "unique, NEST-00001 format"
    uuid tenant_id FK
    uuid unit_id FK
    string term_type "DAILY|MONTHLY|SIX_MONTHS|TWELVE_MONTHS"
    date start_date
    date end_date "nullable"
    decimal initial_price "auto-set from unit pricing"
    decimal deal_price "nullable, negotiated price"
    string currency "default IDR"
    string status "DRAFT|IN_PROGRESS|INVOICE_REQUESTED|INVOICE_UPLOADED|COMPLETED|CANCELLED"
    string current_step "journey step tracker"
    string blocked_reason "nullable"
    datetime invoice_requested_at "nullable"
    datetime cancelled_at "nullable"
    text cancellation_reason "nullable"
    date move_in_date "nullable"
    text move_in_notes "nullable"
    datetime created_at
    datetime updated_at
  }

  DOCUMENTS {
    uuid id PK
    uuid deal_id FK
    string doc_type "BOOKING_CONFIRMATION|LOO_DRAFT|LOO_FINAL|LEASE_AGREEMENT|OFFICIAL_CONFIRMATION|MOVE_IN_CONFIRMATION|UNIT_HANDOVER"
    int latest_version
    datetime created_at
  }

  DOCUMENT_VERSIONS {
    uuid id PK
    uuid document_id FK
    int version_no
    string html_path "relative file path"
    string pdf_path "relative file path"
    string signatory_name "nullable"
    string signatory_title "nullable"
    string channel "WEB|WHATSAPP, default WEB"
    boolean is_latest "default true"
    datetime generated_at
  }

  FINANCE_ATTACHMENTS {
    uuid id PK
    uuid deal_id FK
    string attachment_type "INVOICE"
    string file_name
    string file_path "relative file path"
    string channel "default WEB"
    datetime uploaded_at
  }

  STATIC_DOCUMENTS {
    uuid id PK
    string doc_type "unique, CATALOG|PRICELIST"
    uuid active_version_id "nullable"
    datetime created_at
  }

  STATIC_DOCUMENT_VERSIONS {
    uuid id PK
    uuid static_document_id FK
    int version_no
    string file_name
    string file_path "relative file path"
    text notes "nullable"
    datetime uploaded_at
    boolean is_active "default false"
  }

  APP_SETTINGS {
    uuid id PK
    string company_legal_name "default NEST Serviced Apartment"
    text company_address "nullable"
    string logo_path "nullable"
    string signatory_name
    string signatory_title
    string signature_image_path "nullable"
    string finance_email "default finance@example.com"
    string bot_whatsapp_number "nullable"
    datetime updated_at
  }

  AUDIT_LOGS {
    uuid id PK
    uuid deal_id FK "nullable"
    string actor "default ADMIN"
    string channel "WEB|WHATSAPP, default WEB"
    string executor "WEB|CLAWDBOT, default WEB"
    string action "CREATE_DEAL|UPDATE_DEAL|PROGRESS_DEAL|GENERATE_DOCUMENT|SET_DEAL_PRICE|SET_MOVE_IN_DETAILS|REQUEST_INVOICE|UPLOAD_INVOICE|CANCEL_DEAL|EMERGENCY_OVERRIDE|UPLOAD_STATIC_DOCUMENT|ACTIVATE_STATIC_DOCUMENT"
    text summary
    json metadata_json "nullable"
    datetime created_at
  }
```

## Simplifications from Original ERD

| Original PRD Design | Actual Implementation | Rationale |
|---|---|---|
| `ADMINS` table | No table — env vars (`ADMIN_USER`, `ADMIN_PASSWORD`) with JWT auth | Single admin user, no need for DB-managed users |
| `UNIT_PRICING` table | Pricing columns inline on `UNITS` (`daily_price`, `monthly_price`, etc.) | One price per term per unit is sufficient |
| `COMPANY_SETTINGS` + `FINANCE_SETTINGS` + `BOT_SETTINGS` | Single `APP_SETTINGS` table | All settings managed by same admin, single row |
| `SIGNATURE_ASSETS` table | `signature_image_path` on `APP_SETTINGS` | One active signature is enough for Phase 1 |
| `DEAL_DOCUMENTS` + `DEAL_DOCUMENT_VERSIONS` | `DOCUMENTS` + `DOCUMENT_VERSIONS` | Simplified naming, same behavior |
| `LIBRARY_DOCUMENTS` + `LIBRARY_DOCUMENT_VERSIONS` | `STATIC_DOCUMENTS` + `STATIC_DOCUMENT_VERSIONS` | Simplified naming, same behavior |
| Deal `list_price` | Deal `initial_price` | Renamed for clarity (auto-set from unit price at deal creation) |
| Deal `status` values BLOCKED/CLOSED | DRAFT/IN_PROGRESS/INVOICE_REQUESTED/INVOICE_UPLOADED/COMPLETED/CANCELLED | More granular statuses reflecting actual workflow |
| Unit status MAINTENANCE | Removed | Not needed in Phase 1 |

## Authentication Model

- No `ADMINS` table in database
- Admin credentials stored as environment variables
- JWT tokens (HS256) with 24-hour expiry, signed with `API_SECRET_KEY`
- Login via `POST /auth/login` returns Bearer token
- All protected endpoints validate token via `Authorization: Bearer <token>` header
- Document preview/download endpoints also accept `?token=<jwt>` query parameter
