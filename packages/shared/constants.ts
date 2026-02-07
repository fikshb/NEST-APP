/**
 * NestApp Shared Constants — Single Source of Truth
 * Generated once; imported by web app and mirrored in Python.
 */

// ── Deal Types ──
export const DEAL_TYPES = ["DAILY", "MONTHLY", "SIX_MONTHS", "TWELVE_MONTHS"] as const;
export type DealType = (typeof DEAL_TYPES)[number];

export const DEAL_TYPE_LABELS: Record<DealType, string> = {
  DAILY: "Daily",
  MONTHLY: "Monthly",
  SIX_MONTHS: "6 Months",
  TWELVE_MONTHS: "12 Months",
};

// ── Deal Statuses ──
export const DEAL_STATUSES = [
  "DRAFT",
  "IN_PROGRESS",
  "INVOICE_REQUESTED",
  "INVOICE_UPLOADED",
  "COMPLETED",
  "CANCELLED",
] as const;
export type DealStatus = (typeof DEAL_STATUSES)[number];

export const DEAL_STATUS_LABELS: Record<DealStatus, string> = {
  DRAFT: "Draft",
  IN_PROGRESS: "In Progress",
  INVOICE_REQUESTED: "Invoice Requested",
  INVOICE_UPLOADED: "Invoice Uploaded",
  COMPLETED: "Completed",
  CANCELLED: "Cancelled",
};

// ── Unit Statuses ──
export const UNIT_STATUSES = ["AVAILABLE", "RESERVED", "OCCUPIED"] as const;
export type UnitStatus = (typeof UNIT_STATUSES)[number];

export const UNIT_STATUS_LABELS: Record<UnitStatus, string> = {
  AVAILABLE: "Available",
  RESERVED: "Reserved",
  OCCUPIED: "Occupied",
};

// ── Document Types (system-generated) ──
export const DOCUMENT_TYPES = [
  "BOOKING_CONFIRMATION",
  "LOO_DRAFT",
  "LOO_FINAL",
  "LEASE_AGREEMENT",
  "OFFICIAL_CONFIRMATION",
  "MOVE_IN_CONFIRMATION",
  "UNIT_HANDOVER",
] as const;
export type DocumentType = (typeof DOCUMENT_TYPES)[number];

export const DOCUMENT_TYPE_LABELS: Record<DocumentType, string> = {
  BOOKING_CONFIRMATION: "Booking Confirmation",
  LOO_DRAFT: "Letter of Offer – Draft",
  LOO_FINAL: "Letter of Offer – Final",
  LEASE_AGREEMENT: "Lease Agreement",
  OFFICIAL_CONFIRMATION: "Official Confirmation Letter",
  MOVE_IN_CONFIRMATION: "Move-in Confirmation",
  UNIT_HANDOVER: "Unit Handover Certificate",
};

// ── Static Document Types ──
export const STATIC_DOCUMENT_TYPES = ["CATALOG", "PRICELIST"] as const;
export type StaticDocumentType = (typeof STATIC_DOCUMENT_TYPES)[number];

// ── Journey Steps ──
export const DAILY_JOURNEY_STEPS = [
  "SELECT_UNIT",
  "GENERATE_BOOKING_CONFIRMATION",
  "GENERATE_OFFICIAL_CONFIRMATION",
  "REQUEST_INVOICE",
  "UPLOAD_INVOICE",
  "GENERATE_HANDOVER",
  "DEAL_CLOSED",
] as const;
export type DailyJourneyStep = (typeof DAILY_JOURNEY_STEPS)[number];

export const MONTHLY_JOURNEY_STEPS = [
  "SELECT_UNIT",
  "GENERATE_LOO_DRAFT",
  "FINALIZE_LOO",
  "GENERATE_LEASE_AGREEMENT",
  "GENERATE_OFFICIAL_CONFIRMATION",
  "REQUEST_INVOICE",
  "UPLOAD_INVOICE",
  "GENERATE_MOVE_IN",
  "GENERATE_HANDOVER",
  "DEAL_CLOSED",
] as const;
export type MonthlyJourneyStep = (typeof MONTHLY_JOURNEY_STEPS)[number];

export type JourneyStep = DailyJourneyStep | MonthlyJourneyStep;

export const JOURNEY_STEP_LABELS: Record<string, string> = {
  SELECT_UNIT: "Select Unit",
  GENERATE_BOOKING_CONFIRMATION: "Generate Booking Confirmation",
  GENERATE_OFFICIAL_CONFIRMATION: "Generate Official Confirmation Letter",
  REQUEST_INVOICE: "Request Invoice",
  UPLOAD_INVOICE: "Upload Invoice",
  GENERATE_HANDOVER: "Generate Unit Handover Certificate",
  DEAL_CLOSED: "Deal Closed",
  GENERATE_LOO_DRAFT: "Generate Offer (LOO Draft)",
  FINALIZE_LOO: "Finalize Offer (LOO Final)",
  GENERATE_LEASE_AGREEMENT: "Generate Lease Agreement",
  GENERATE_MOVE_IN: "Generate Move-in Confirmation",
};

// Map journey steps to their required document type (if any)
export const STEP_DOCUMENT_MAP: Partial<Record<string, DocumentType>> = {
  GENERATE_BOOKING_CONFIRMATION: "BOOKING_CONFIRMATION",
  GENERATE_LOO_DRAFT: "LOO_DRAFT",
  FINALIZE_LOO: "LOO_FINAL",
  GENERATE_LEASE_AGREEMENT: "LEASE_AGREEMENT",
  GENERATE_OFFICIAL_CONFIRMATION: "OFFICIAL_CONFIRMATION",
  GENERATE_MOVE_IN: "MOVE_IN_CONFIRMATION",
  GENERATE_HANDOVER: "UNIT_HANDOVER",
};

// ── Audit Action Types ──
export const AUDIT_ACTIONS = [
  "CREATE_DEAL",
  "UPDATE_DEAL",
  "PROGRESS_DEAL",
  "CANCEL_DEAL",
  "EMERGENCY_OVERRIDE",
  "GENERATE_DOCUMENT",
  "REQUEST_INVOICE",
  "UPLOAD_INVOICE",
  "CREATE_TENANT",
  "UPDATE_TENANT",
  "CREATE_UNIT",
  "UPDATE_UNIT",
  "UPLOAD_STATIC_DOCUMENT",
  "ACTIVATE_STATIC_DOCUMENT",
  "UPDATE_SETTINGS",
] as const;
export type AuditAction = (typeof AUDIT_ACTIONS)[number];

// ── Channels ──
export const CHANNELS = ["WEB", "WHATSAPP"] as const;
export type Channel = (typeof CHANNELS)[number];

// ── Finance Attachment Types ──
export const FINANCE_ATTACHMENT_TYPES = ["INVOICE", "RECEIPT"] as const;
export type FinanceAttachmentType = (typeof FINANCE_ATTACHMENT_TYPES)[number];
