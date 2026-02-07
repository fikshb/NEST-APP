flowchart LR
  %% Actors
  A[Admin] -->|Web UI| W[NestApp Web]
  A -->|WhatsApp| B[ClawdBot (OpenClaw)]
  T[Tenant] -->|WhatsApp| B
  F[Finance Holding] -->|Email (Invoice/Receipt)| A

  %% Core system
  W -->|REST API| API[NestApp Backend API]
  B -->|REST API (acting on behalf of Admin)| API

  %% Storage
  API --> DB[(PostgreSQL)]
  API --> FS[(File Storage: S3/Local)]
  API --> MAIL[Email Service (SMTP/Provider)]

  %% Document flows
  API -->|Generate HTML + PDF| FS
  FS -->|Secure URLs| API

  %% Library flows
  W -->|Manage Library PDFs| API
  API -->|Catalog/Pricelist versions| DB
  API -->|Store PDF files| FS

  %% Finance request flow
  API -->|Send Invoice Request Email| MAIL
  MAIL -->|Email to Finance| F
  F -->|Invoice/Receipt email to Admin| A
  A -->|Upload Invoice/Receipt| W

  %% Notes
  classDef core fill:#111,color:#fff,stroke:#333;
  class API,DB,FS,MAIL core;

## Daily Flow

sequenceDiagram
  autonumber
  participant Tenant
  participant Bot as ClawdBot (WA)
  participant App as NestApp (API)
  participant Admin as Admin (Web)
  participant Finance as Finance Holding (Email)

  Tenant->>Bot: Request catalog
  Bot->>App: GET /library/catalog/active
  App-->>Bot: Catalog PDF URL
  Bot-->>Tenant: Send Catalog PDF

  Tenant->>Bot: Request pricelist
  Bot->>App: GET /library/pricelist/active
  App-->>Bot: Pricelist PDF URL
  Bot-->>Tenant: Send Pricelist PDF

  Tenant->>Bot: Select unit + dates (Daily)
  Bot->>App: POST /deals (tenant, unit, dates, term=DAILY)
  App-->>Bot: Deal ID

  Bot->>App: POST /deals/{id}/documents/booking-confirmation
  App-->>Bot: Booking Confirmation PDF URL
  Bot-->>Tenant: Send Booking Confirmation

  Bot->>App: POST /deals/{id}/documents/official-confirmation
  App-->>Bot: Official Confirmation Letter PDF URL
  Bot-->>Tenant: Send Official Confirmation Letter

  Bot-->>Admin: Notify "Ready to request invoice" (optional)

  Admin->>App: Click "Request Invoice"
  App->>Finance: Send invoice request email (auto)
  App-->>Admin: Status = Invoice Requested

  Finance-->>Admin: Email Invoice PDF
  Admin->>App: Upload Invoice (INVOICE)
  App-->>Admin: Status = Invoice Uploaded

  Admin-->>Bot: Ask bot to send invoice to tenant (optional)
  Bot->>App: GET Invoice file URL (latest)
  App-->>Bot: Invoice URL
  Bot-->>Tenant: Send Invoice PDF

  Bot->>App: POST /deals/{id}/documents/handover
  App-->>Bot: Handover Certificate PDF URL
  Bot-->>Tenant: Send Handover Certificate (optional)

  App-->>Admin: Deal can be closed

## Monthly Flow

sequenceDiagram
  autonumber
  participant Tenant
  participant Bot as ClawdBot (WA)
  participant App as NestApp (API)
  participant Admin as Admin (Web)
  participant Finance as Finance Holding (Email)

  Tenant->>Bot: Request catalog + pricelist
  Bot->>App: GET /library/catalog/active
  App-->>Bot: Catalog URL
  Bot-->>Tenant: Send Catalog
  Bot->>App: GET /library/pricelist/active
  App-->>Bot: Pricelist URL
  Bot-->>Tenant: Send Pricelist

  Tenant->>Bot: Select unit + period (Monthly/6/12)
  Bot->>App: POST /deals (term=MONTHLY/6M/12M)
  App-->>Bot: Deal ID

  Bot->>Tenant: Collect tenant details (name/email/company/ID optional)
  Bot->>App: PATCH /deals/{id} (tenant details, notes)

  Bot->>App: POST /deals/{id}/documents/loo-draft
  App-->>Bot: LOO Draft PDF URL
  Bot-->>Tenant: Send LOO Draft

  Tenant->>Bot: Negotiate (optional)
  Bot->>App: PATCH /deals/{id} (deal_price updates)
  App-->>Bot: OK

  Bot->>App: POST /deals/{id}/documents/loo-final
  App-->>Bot: LOO Final PDF URL
  Bot-->>Tenant: Send LOO Final

  Bot->>App: POST /deals/{id}/documents/lease-agreement
  App-->>Bot: Lease Agreement PDF URL
  Bot-->>Tenant: Send Lease Agreement

  Bot->>App: POST /deals/{id}/documents/official-confirmation
  App-->>Bot: Official Confirmation Letter URL
  Bot-->>Tenant: Send Official Confirmation Letter

  Bot-->>Admin: Notify "Ready to request invoice" (optional)

  Admin->>App: Click "Request Invoice"
  App->>Finance: Send invoice request email (auto)
  App-->>Admin: Status = Invoice Requested

  Finance-->>Admin: Email Invoice PDF
  Admin->>App: Upload Invoice (INVOICE)
  App-->>Admin: Status = Invoice Uploaded

  Bot->>App: POST /deals/{id}/documents/move-in
  App-->>Bot: Move-in Confirmation PDF URL
  Bot-->>Tenant: Send Move-in Confirmation

  Bot->>App: POST /deals/{id}/documents/handover
  App-->>Bot: Handover Certificate PDF URL
  Bot-->>Tenant: Send Handover Certificate (optional)

  App-->>Admin: Deal can be closed
