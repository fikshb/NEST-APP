erDiagram
  ADMINS ||--|| COMPANY_SETTINGS : configures
  ADMINS ||--|| FINANCE_SETTINGS : configures
  ADMINS ||--|| BOT_SETTINGS : configures
  ADMINS ||--|| SIGNATURE_ASSETS : uploads

  ADMINS ||--o{ DEALS : creates_updates
  TENANTS ||--o{ DEALS : participates_in
  UNITS ||--o{ DEALS : booked_for

  DEALS ||--o{ DEAL_DOCUMENTS : has
  DEAL_DOCUMENTS ||--o{ DEAL_DOCUMENT_VERSIONS : versions

  DEALS ||--o{ FINANCE_ATTACHMENTS : has
  ADMINS ||--o{ FINANCE_ATTACHMENTS : uploads

  ADMINS ||--o{ AUDIT_LOGS : generates
  DEALS ||--o{ AUDIT_LOGS : has

  ADMINS ||--o{ LIBRARY_DOCUMENTS : uploads
  LIBRARY_DOCUMENTS ||--o{ LIBRARY_DOCUMENT_VERSIONS : versions

  UNITS ||--o{ UNIT_PRICING : has

  ADMINS {
    uuid id PK
    string email
    string full_name
    datetime created_at
    datetime updated_at
  }

  TENANTS {
    uuid id PK
    string full_name
    string phone
    string email
    string company_name
    text notes
    datetime created_at
    datetime updated_at
  }

  UNITS {
    uuid id PK
    string unit_code
    string unit_type
    string status "AVAILABLE|RESERVED|OCCUPIED|MAINTENANCE"
    text notes
    datetime created_at
    datetime updated_at
  }

  UNIT_PRICING {
    uuid id PK
    uuid unit_id FK
    string term_type "DAILY|MONTHLY|6M|12M"
    decimal default_price
    string currency "IDR"
    datetime updated_at
  }

  DEALS {
    uuid id PK
    string deal_code "human-friendly reference"
    uuid tenant_id FK
    uuid unit_id FK
    string term_type "DAILY|MONTHLY|6M|12M"
    date start_date
    date end_date
    decimal list_price
    decimal deal_price
    string currency "IDR"
    string status "IN_PROGRESS|BLOCKED|CANCELLED|CLOSED"
    string blocked_reason
    boolean invoice_requested
    datetime invoice_requested_at
    datetime cancelled_at
    text cancellation_reason
    datetime created_at
    datetime updated_at
  }

  DEAL_DOCUMENTS {
    uuid id PK
    uuid deal_id FK
    string doc_type "BOOKING_CONFIRMATION|LOO_DRAFT|LOO_FINAL|LEASE_AGREEMENT|OFFICIAL_CONFIRMATION|MOVE_IN|HANDOVER"
    string state "MISSING|GENERATED"
    uuid latest_version_id
    datetime last_generated_at
  }

  DEAL_DOCUMENT_VERSIONS {
    uuid id PK
    uuid deal_document_id FK
    int version_no
    string html_storage_key
    string pdf_storage_key
    string preview_url
    string pdf_url
    uuid signature_asset_id FK
    string signatory_name
    string signatory_title
    datetime generated_at
    uuid generated_by_admin_id FK
    string channel "WEB|WHATSAPP"
    boolean is_latest
  }

  FINANCE_ATTACHMENTS {
    uuid id PK
    uuid deal_id FK
    string doc_type "INVOICE|RECEIPT"
    string file_name
    string file_storage_key
    string file_url
    datetime uploaded_at
    uuid uploaded_by_admin_id FK
    string channel "WEB|WHATSAPP"
  }

  LIBRARY_DOCUMENTS {
    uuid id PK
    string doc_type "CATALOG|PRICELIST"
    uuid active_version_id
    datetime created_at
  }

  LIBRARY_DOCUMENT_VERSIONS {
    uuid id PK
    uuid library_document_id FK
    int version_no
    string file_name
    string file_storage_key
    string file_url
    text notes
    datetime uploaded_at
    uuid uploaded_by_admin_id FK
    boolean is_active
  }

  COMPANY_SETTINGS {
    uuid id PK
    uuid admin_id FK
    string legal_name
    string address
    string logo_storage_key
    string logo_url
    string default_footer_text
    string signatory_name
    string signatory_title
    uuid signature_asset_id FK
    datetime updated_at
  }

  FINANCE_SETTINGS {
    uuid id PK
    uuid admin_id FK
    string finance_company_name
    string finance_email_to
    string finance_email_cc
    string email_subject_template
    text email_body_template
    datetime updated_at
  }

  BOT_SETTINGS {
    uuid id PK
    uuid admin_id FK
    string bot_display_name
    string bot_whatsapp_number
    string service_token_hash
    datetime updated_at
  }

  SIGNATURE_ASSETS {
    uuid id PK
    uuid uploaded_by_admin_id FK
    string file_name
    string file_storage_key
    string file_url
    int version_no
    boolean is_active
    datetime uploaded_at
  }

  AUDIT_LOGS {
    uuid id PK
    uuid admin_id FK
    uuid deal_id FK
    string actor "ADMIN"
    string executor "WEB|CLAWDBOT"
    string action_type "CREATE_DEAL|UPDATE_DEAL|GENERATE_DOC|UPLOAD_FINANCE_DOC|REQUEST_INVOICE|CANCEL_DEAL|EMERGENCY_OVERRIDE|ACTIVATE_LIBRARY_DOC"
    text action_summary
    json metadata
    datetime created_at
  }
