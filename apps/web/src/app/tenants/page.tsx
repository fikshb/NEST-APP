"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchTenants, createTenant, updateTenant } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import { Plus, Pencil } from "lucide-react";

export default function TenantsPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const { data: tenants, isLoading } = useQuery({
    queryKey: ["tenants", search],
    queryFn: () => fetchTenants(search || undefined),
  });
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<any>(null);

  const handleSave = async (data: any) => {
    if (editing) {
      await updateTenant(editing.id, data);
    } else {
      await createTenant(data);
    }
    queryClient.invalidateQueries({ queryKey: ["tenants"] });
    setShowForm(false);
    setEditing(null);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-[28px]">Tenants</h2>
        <button
          className="btn-primary gap-2"
          onClick={() => {
            setEditing(null);
            setShowForm(true);
          }}
        >
          <Plus size={16} /> Add Tenant
        </button>
      </div>

      <div className="mb-6">
        <input
          type="text"
          className="input-field max-w-sm"
          placeholder="Search tenants..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {showForm && (
        <TenantForm
          initial={editing}
          onSave={handleSave}
          onCancel={() => {
            setShowForm(false);
            setEditing(null);
          }}
        />
      )}

      {isLoading ? (
        <p className="text-text-muted font-ui">Loading...</p>
      ) : (
        <div className="space-y-3">
          {(tenants || []).map((tenant: any) => (
            <div key={tenant.id} className="card flex items-center justify-between">
              <div>
                <p className="font-ui font-medium text-teal-900">{tenant.full_name}</p>
                <p className="text-sm text-text-secondary">
                  {tenant.email} — {tenant.phone}
                </p>
                {tenant.company_name && (
                  <p className="text-xs text-text-muted mt-1">{tenant.company_name}</p>
                )}
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-text-muted font-ui">
                  {formatDate(tenant.created_at)}
                </span>
                <button
                  className="p-2 rounded-input hover:bg-neutral-softWhite transition-colors"
                  onClick={() => {
                    setEditing(tenant);
                    setShowForm(true);
                  }}
                >
                  <Pencil size={14} className="text-text-secondary" />
                </button>
              </div>
            </div>
          ))}
          {(tenants || []).length === 0 && (
            <p className="text-text-muted font-ui text-center py-12">No tenants found.</p>
          )}
        </div>
      )}
    </div>
  );
}

function TenantForm({
  initial,
  onSave,
  onCancel,
}: {
  initial: any;
  onSave: (data: any) => Promise<void>;
  onCancel: () => void;
}) {
  const [form, setForm] = useState({
    full_name: initial?.full_name || "",
    phone: initial?.phone || "",
    email: initial?.email || "",
    company_name: initial?.company_name || "",
    notes: initial?.notes || "",
  });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async () => {
    if (!form.full_name || !form.phone || !form.email) return;
    setSaving(true);
    await onSave(form);
    setSaving(false);
  };

  return (
    <div className="card mb-6">
      <h4 className="text-lg font-heading font-semibold text-teal-900 mb-4">
        {initial ? "Edit Tenant" : "New Tenant"}
      </h4>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="text-sm font-ui text-text-secondary mb-1 block">Full Name</label>
          <input className="input-field" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
        </div>
        <div>
          <label className="text-sm font-ui text-text-secondary mb-1 block">Phone</label>
          <input className="input-field" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
        </div>
        <div>
          <label className="text-sm font-ui text-text-secondary mb-1 block">Email</label>
          <input className="input-field" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        </div>
        <div>
          <label className="text-sm font-ui text-text-secondary mb-1 block">Company (optional)</label>
          <input className="input-field" value={form.company_name} onChange={(e) => setForm({ ...form, company_name: e.target.value })} />
        </div>
        <div className="sm:col-span-2">
          <label className="text-sm font-ui text-text-secondary mb-1 block">Notes</label>
          <textarea className="input-field" rows={2} value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
        </div>
      </div>
      <div className="flex gap-3 mt-6 justify-end">
        <button className="btn-secondary" onClick={onCancel}>Cancel</button>
        <button className="btn-primary" onClick={handleSubmit} disabled={saving}>
          {saving ? "Saving..." : "Save"}
        </button>
      </div>
    </div>
  );
}
