# System Context & Data Flow — NestApp

## A. System Context Diagram

```mermaid
flowchart LR
  %% Actors
  A[Admin] -->|Web UI| W[NestApp Web]
  A -->|WhatsApp| B[ClawdBot via OpenClaw]
  T[Tenant] -->|WhatsApp| B
  F[Finance Holding] -->|Email Invoice/Receipt| A

  %% Auth
  W -->|POST /auth/login| API[NestApp Backend API]
  W -->|JWT Bearer token| API

  %% Core system
  W -->|REST API| API
  B -->|REST API acting on behalf of Admin| API

  %% Storage
  API --> DB[(PostgreSQL)]
  API --> FS[(File Storage: Local)]
  API --> MAIL[Email Service SMTP stub]

  %% Document flows
  API -->|Generate HTML + PDF via WeasyPrint| FS
  FS -->|Serve via token URL| API

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
```

---

## B. Authentication Flow

```mermaid
sequenceDiagram
  participant Admin
  participant Web as NestApp Web
  participant API as NestApp API

  Admin->>Web: Open http://localhost:3000
  Web->>Web: Check localStorage for token
  alt No token
    Web-->>Admin: Redirect to /login
    Admin->>Web: Enter username + password
    Web->>API: POST /auth/login
    API-->>Web: JWT access_token (24h expiry)
    Web->>Web: Store token in localStorage
    Web-->>Admin: Redirect to Dashboard
  else Has token
    Web->>API: GET /dashboard (Bearer token)
    API-->>Web: Dashboard data
    Web-->>Admin: Show Dashboard
  end
```

---

## C. Daily Stay Flow (5 Steps)

```mermaid
sequenceDiagram
  autonumber
  participant Tenant
  participant Bot as ClawdBot (WA)
  participant App as NestApp (API)
  participant Admin as Admin (Web)
  participant Finance as Finance Holding (Email)

  Tenant->>Bot: Request catalog
  Bot->>App: GET /static-documents/CATALOG/active
  App-->>Bot: Catalog PDF
  Bot-->>Tenant: Send Catalog PDF

  Tenant->>Bot: Request pricelist
  Bot->>App: GET /static-documents/PRICELIST/active
  App-->>Bot: Pricelist PDF
  Bot-->>Tenant: Send Pricelist PDF

  Tenant->>Bot: Select unit + dates (Daily)
  Bot->>App: POST /deals (tenant, unit, dates, term=DAILY)
  App-->>Bot: Deal created (step: GENERATE_BOOKING_CONFIRMATION)

  Note over Admin,App: Optional: set negotiated price
  Admin->>App: POST /deals/{id}/actions/set-deal-price
  App-->>Admin: Price updated

  Bot->>App: POST /deals/{id}/actions/generate-document
  App-->>Bot: Booking Confirmation PDF
  Bot-->>Tenant: Send Booking Confirmation

  Bot-->>Admin: Notify "Ready to request invoice" (optional)

  Admin->>App: POST /deals/{id}/actions/request-invoice
  App->>Finance: Send invoice request email (auto)
  App-->>Admin: Status = Invoice Requested

  Finance-->>Admin: Email Invoice PDF
  Admin->>App: POST /deals/{id}/actions/upload-invoice
  App-->>Admin: Status = Invoice Uploaded, step = DEAL_CLOSED

  Admin->>App: POST /deals/{id}/actions/close
  App-->>Admin: Deal completed, unit = OCCUPIED
```

---

## D. Monthly / 6M / 12M Flow (10 Steps)

```mermaid
sequenceDiagram
  autonumber
  participant Tenant
  participant Bot as ClawdBot (WA)
  participant App as NestApp (API)
  participant Admin as Admin (Web)
  participant Finance as Finance Holding (Email)

  Tenant->>Bot: Request catalog + pricelist
  Bot->>App: GET /static-documents/CATALOG/active
  App-->>Bot: Catalog PDF
  Bot-->>Tenant: Send Catalog
  Bot->>App: GET /static-documents/PRICELIST/active
  App-->>Bot: Pricelist PDF
  Bot-->>Tenant: Send Pricelist

  Tenant->>Bot: Select unit + period (Monthly/6M/12M)
  Bot->>App: POST /deals (term=MONTHLY/SIX_MONTHS/TWELVE_MONTHS)
  App-->>Bot: Deal created (step: GENERATE_LOO_DRAFT)

  Bot->>App: POST /deals/{id}/actions/generate-document
  App-->>Bot: LOO Draft PDF
  Bot-->>Tenant: Send LOO Draft

  Tenant->>Bot: Negotiate price (optional)
  Admin->>App: POST /deals/{id}/actions/set-deal-price
  App-->>Admin: Negotiated price saved

  Bot->>App: POST /deals/{id}/actions/generate-document
  App-->>Bot: LOO Final PDF (with deal_price or initial_price)
  Bot-->>Tenant: Send LOO Final

  Bot->>App: POST /deals/{id}/actions/generate-document
  App-->>Bot: Lease Agreement PDF
  Bot-->>Tenant: Send Lease Agreement

  Bot->>App: POST /deals/{id}/actions/generate-document
  App-->>Bot: Official Confirmation Letter PDF
  Bot-->>Tenant: Send Official Confirmation Letter

  Bot-->>Admin: Notify "Ready to request invoice"

  Admin->>App: POST /deals/{id}/actions/request-invoice
  App->>Finance: Send invoice request email (auto)
  App-->>Admin: Status = Invoice Requested

  Finance-->>Admin: Email Invoice PDF
  Admin->>App: POST /deals/{id}/actions/upload-invoice
  App-->>Admin: Status = Invoice Uploaded

  Note over Admin,App: Set move-in date + items
  Admin->>App: POST /deals/{id}/actions/set-move-in-details
  App-->>Admin: Move-in details saved

  Bot->>App: POST /deals/{id}/actions/generate-document
  App-->>Bot: Move-in Confirmation PDF
  Bot-->>Tenant: Send Move-in Confirmation

  Bot->>App: POST /deals/{id}/actions/generate-document
  App-->>Bot: Unit Handover Certificate PDF
  Bot-->>Tenant: Send Handover Certificate

  Admin->>App: POST /deals/{id}/actions/close
  App-->>Admin: Deal completed, unit = OCCUPIED
```

---

## E. Document Generation Flow

```mermaid
flowchart TD
  A[Admin clicks Generate / Bot triggers] --> B[API: generate-document action]
  B --> C{Current step in STEP_DOCUMENT_MAP?}
  C -->|No| E[Return 400: step doesn't require doc]
  C -->|Yes| D[Determine doc_type from step]
  D --> F[Load Jinja2 template]
  F --> G[Render HTML with deal/tenant/unit/company data]
  G --> H[Embed logo + signature as base64]
  H --> I[Save HTML to storage]
  I --> J[WeasyPrint: Convert HTML to PDF]
  J --> K[Save PDF to storage]
  K --> L[Create DocumentVersion record]
  L --> M[Advance deal to next journey step]
  M --> N[Log audit entry]
```

**File naming format:** `{DocName}_{TenantName}_{UnitCode}_{Date}_v{Version}.pdf`
Example: `Booking-Confirmation_John-Doe_101_2026-02-07_v1.pdf`
