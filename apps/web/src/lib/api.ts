const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `API error: ${res.status}`);
  }
  return res.json();
}

// ── Dashboard ──
export const fetchDashboard = () => apiFetch<any>("/dashboard");

// ── Tenants ──
export const fetchTenants = (search?: string) =>
  apiFetch<any[]>(`/tenants${search ? `?search=${encodeURIComponent(search)}` : ""}`);
export const fetchTenant = (id: string) => apiFetch<any>(`/tenants/${id}`);
export const createTenant = (data: any) =>
  apiFetch<any>("/tenants", { method: "POST", body: JSON.stringify(data) });
export const updateTenant = (id: string, data: any) =>
  apiFetch<any>(`/tenants/${id}`, { method: "PUT", body: JSON.stringify(data) });

// ── Units ──
export const fetchUnits = (status?: string) =>
  apiFetch<any[]>(`/units${status ? `?status=${status}` : ""}`);
export const fetchUnit = (id: string) => apiFetch<any>(`/units/${id}`);
export const createUnit = (data: any) =>
  apiFetch<any>("/units", { method: "POST", body: JSON.stringify(data) });
export const updateUnit = (id: string, data: any) =>
  apiFetch<any>(`/units/${id}`, { method: "PUT", body: JSON.stringify(data) });

// ── Deals ──
export const fetchDeals = (status?: string) =>
  apiFetch<any[]>(`/deals${status ? `?status=${status}` : ""}`);
export const fetchDeal = (id: string) => apiFetch<any>(`/deals/${id}`);
export const fetchDealJourney = (id: string) => apiFetch<any>(`/deals/${id}/journey`);
export const createDeal = (data: any) =>
  apiFetch<any>("/deals", { method: "POST", body: JSON.stringify(data) });
export const updateDeal = (id: string, data: any) =>
  apiFetch<any>(`/deals/${id}`, { method: "PATCH", body: JSON.stringify(data) });

// ── Deal Actions ──
export const dealGenerateDocument = (id: string) =>
  apiFetch<any>(`/deals/${id}/actions/generate-document`, { method: "POST" });
export const dealRequestInvoice = (id: string) =>
  apiFetch<any>(`/deals/${id}/actions/request-invoice`, { method: "POST" });
export const dealUploadInvoice = (id: string, file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  return fetch(`${API_BASE}/deals/${id}/actions/upload-invoice`, {
    method: "POST",
    body: formData,
  }).then((res) => {
    if (!res.ok) throw new Error("Upload failed");
    return res.json();
  });
};
export const dealClose = (id: string) =>
  apiFetch<any>(`/deals/${id}/actions/close`, { method: "POST" });
export const dealCancel = (id: string, reason: string) =>
  apiFetch<any>(`/deals/${id}/actions/cancel`, { method: "POST", body: JSON.stringify({ reason }) });
export const dealEmergencyOverride = (id: string, reason: string, targetStep: string) =>
  apiFetch<any>(`/deals/${id}/actions/emergency-override`, {
    method: "POST",
    body: JSON.stringify({ reason, target_step: targetStep }),
  });

// ── Documents ──
export const fetchDocuments = (dealId?: string) =>
  apiFetch<any[]>(`/documents${dealId ? `?deal_id=${dealId}` : ""}`);

// ── Static Documents ──
export const fetchStaticDocuments = () => apiFetch<any[]>("/static-documents");
export const uploadStaticDocument = (docType: string, file: File, notes?: string) => {
  const formData = new FormData();
  formData.append("file", file);
  if (notes) formData.append("notes", notes);
  return fetch(`${API_BASE}/static-documents/${docType}/upload`, {
    method: "POST",
    body: formData,
  }).then((res) => {
    if (!res.ok) throw new Error("Upload failed");
    return res.json();
  });
};

// ── Settings ──
export const fetchSettings = () => apiFetch<any>("/settings");
export const updateSettings = (data: any) =>
  apiFetch<any>("/settings", { method: "PUT", body: JSON.stringify(data) });

// ── Audit Logs ──
export const fetchAuditLogs = (params?: { deal_id?: string; page?: number }) => {
  const qs = new URLSearchParams();
  if (params?.deal_id) qs.set("deal_id", params.deal_id);
  if (params?.page) qs.set("page", String(params.page));
  return apiFetch<any[]>(`/audit-logs?${qs.toString()}`);
};
