/**
 * NestApp Shared Types — API contract types shared between frontend and backend.
 */
import type {
  DealType,
  DealStatus,
  UnitStatus,
  DocumentType,
  StaticDocumentType,
  Channel,
  AuditAction,
  FinanceAttachmentType,
} from "./constants";

// ── Tenant ──
export interface Tenant {
  id: string;
  full_name: string;
  phone: string;
  email: string;
  company_name: string | null;
  notes: string | null;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface TenantCreate {
  full_name: string;
  phone: string;
  email: string;
  company_name?: string;
  notes?: string;
}

export interface TenantUpdate {
  full_name?: string;
  phone?: string;
  email?: string;
  company_name?: string | null;
  notes?: string | null;
}

// ── Unit ──
export interface Unit {
  id: string;
  unit_code: string;
  unit_type: string;
  status: UnitStatus;
  notes: string | null;
  daily_price: number | null;
  monthly_price: number | null;
  six_month_price: number | null;
  twelve_month_price: number | null;
  currency: string;
  created_at: string;
  updated_at: string;
}

export interface UnitCreate {
  unit_code: string;
  unit_type: string;
  notes?: string;
  daily_price?: number;
  monthly_price?: number;
  six_month_price?: number;
  twelve_month_price?: number;
  currency?: string;
}

export interface UnitUpdate {
  unit_code?: string;
  unit_type?: string;
  notes?: string | null;
  daily_price?: number | null;
  monthly_price?: number | null;
  six_month_price?: number | null;
  twelve_month_price?: number | null;
}

// ── Deal ──
export interface Deal {
  id: string;
  deal_code: string;
  tenant_id: string;
  unit_id: string;
  term_type: DealType;
  start_date: string;
  end_date: string | null;
  list_price: number;
  deal_price: number;
  currency: string;
  status: DealStatus;
  current_step: string;
  blocked_reason: string | null;
  invoice_requested_at: string | null;
  cancelled_at: string | null;
  cancellation_reason: string | null;
  created_at: string;
  updated_at: string;
  tenant?: Tenant;
  unit?: Unit;
}

export interface DealCreate {
  tenant_id: string;
  unit_id: string;
  term_type: DealType;
  start_date: string;
  end_date?: string;
  list_price: number;
  deal_price: number;
  currency?: string;
}

export interface DealUpdate {
  deal_price?: number;
  start_date?: string;
  end_date?: string;
  notes?: string;
}

// ── Document ──
export interface Document {
  id: string;
  deal_id: string;
  doc_type: DocumentType;
  latest_version: number;
  versions: DocumentVersion[];
  created_at: string;
}

export interface DocumentVersion {
  id: string;
  version_no: number;
  html_path: string;
  pdf_path: string;
  channel: Channel;
  generated_at: string;
  is_latest: boolean;
}

// ── Static Document ──
export interface StaticDocument {
  id: string;
  doc_type: StaticDocumentType;
  active_version_id: string | null;
  versions: StaticDocumentVersion[];
  created_at: string;
}

export interface StaticDocumentVersion {
  id: string;
  version_no: number;
  file_name: string;
  file_path: string;
  notes: string | null;
  uploaded_at: string;
  is_active: boolean;
}

// ── Finance Attachment ──
export interface FinanceAttachment {
  id: string;
  deal_id: string;
  attachment_type: FinanceAttachmentType;
  file_name: string;
  file_path: string;
  uploaded_at: string;
  channel: Channel;
}

// ── Settings ──
export interface Settings {
  id: string;
  company_legal_name: string;
  company_address: string;
  logo_path: string | null;
  signatory_name: string;
  signatory_title: string;
  signature_image_path: string | null;
  finance_email: string;
  bot_whatsapp_number: string;
  updated_at: string;
}

// ── Audit Log ──
export interface AuditLog {
  id: string;
  deal_id: string | null;
  actor: string;
  channel: Channel;
  executor: string;
  action: AuditAction;
  summary: string;
  metadata: Record<string, unknown> | null;
  created_at: string;
}

// ── Dashboard ──
export interface DashboardSummary {
  deals_in_progress: number;
  deals_blocked: number;
  deals_awaiting_action: number;
  deals_completed: number;
  unit_occupancy: {
    available: number;
    reserved: number;
    occupied: number;
  };
  deal_status_chart: {
    in_progress: number;
    invoice_requested: number;
    completed: number;
  };
}

// ── API Response Wrappers ──
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}

export interface ActionResponse {
  success: boolean;
  message: string;
  deal?: Deal;
  document?: Document;
}
