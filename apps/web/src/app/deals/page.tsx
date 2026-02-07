"use client";

import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { fetchDeals, fetchTenants, fetchUnits, createDeal } from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/utils";
import { Plus } from "lucide-react";

const STATUS_BADGE: Record<string, string> = {
  DRAFT: "badge",
  IN_PROGRESS: "badge badge-info",
  INVOICE_REQUESTED: "badge badge-warning",
  INVOICE_UPLOADED: "badge badge-info",
  COMPLETED: "badge badge-success",
  CANCELLED: "badge badge-danger",
};

const TERM_PRICE_FIELD: Record<string, string> = {
  DAILY: "daily_price",
  MONTHLY: "monthly_price",
  SIX_MONTHS: "six_month_price",
  TWELVE_MONTHS: "twelve_month_price",
};

export default function DealsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const statusFilter = searchParams.get("status") || undefined;

  const { data: deals, isLoading, refetch } = useQuery({
    queryKey: ["deals", statusFilter],
    queryFn: () => fetchDeals(statusFilter),
  });

  const [showCreate, setShowCreate] = useState(false);

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-[28px]">Deals</h2>
        <button className="btn-primary gap-2" onClick={() => setShowCreate(true)}>
          <Plus size={16} /> New Deal
        </button>
      </div>

      {showCreate && (
        <CreateDealModal
          onClose={() => setShowCreate(false)}
          onCreated={() => {
            setShowCreate(false);
            refetch();
          }}
        />
      )}

      {isLoading ? (
        <p className="text-text-muted font-ui">Loading deals...</p>
      ) : (
        <div className="space-y-3">
          {(deals || []).map((deal: any) => (
            <button
              key={deal.id}
              onClick={() => router.push(`/deals/${deal.id}`)}
              className="card w-full text-left hover:shadow-soft transition-shadow flex items-center justify-between"
            >
              <div>
                <p className="font-ui font-medium text-teal-900">{deal.deal_code}</p>
                <p className="text-sm text-text-secondary mt-1">
                  {deal.tenant?.full_name} — Unit {deal.unit?.unit_code} — {deal.term_type.replace(/_/g, " ")}
                </p>
                <p className="text-xs text-text-muted mt-1">
                  Started {formatDate(deal.created_at)} — {formatCurrency(Number(deal.deal_price ?? deal.initial_price), deal.currency)}
                </p>
              </div>
              <span className={STATUS_BADGE[deal.status] || "badge"}>
                {deal.status.replace(/_/g, " ")}
              </span>
            </button>
          ))}
          {(deals || []).length === 0 && (
            <p className="text-text-muted font-ui text-center py-12">
              No deals found.
            </p>
          )}
        </div>
      )}
    </div>
  );
}

function CreateDealModal({
  onClose,
  onCreated,
}: {
  onClose: () => void;
  onCreated: () => void;
}) {
  const { data: tenants } = useQuery({ queryKey: ["tenants"], queryFn: () => fetchTenants() });
  const { data: units } = useQuery({ queryKey: ["units-available"], queryFn: () => fetchUnits("AVAILABLE") });
  const [form, setForm] = useState({
    tenant_id: "",
    unit_id: "",
    term_type: "MONTHLY",
    start_date: new Date().toISOString().split("T")[0],
  });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  // Auto-calculate price from selected unit + term type
  const selectedUnit = useMemo(() => {
    if (!form.unit_id || !units) return null;
    return units.find((u: any) => u.id === form.unit_id);
  }, [form.unit_id, units]);

  const autoPrice = useMemo(() => {
    if (!selectedUnit) return null;
    const field = TERM_PRICE_FIELD[form.term_type];
    if (!field) return null;
    const price = selectedUnit[field];
    return price != null ? Number(price) : null;
  }, [selectedUnit, form.term_type]);

  const handleSubmit = async () => {
    if (!form.tenant_id || !form.unit_id) {
      setError("Please select a tenant and unit.");
      return;
    }
    if (autoPrice === null) {
      setError(`Unit ${selectedUnit?.unit_code} does not have a ${form.term_type.toLowerCase().replace(/_/g, " ")} price configured.`);
      return;
    }
    setSaving(true);
    try {
      await createDeal(form);
      onCreated();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-modal p-8 w-full max-w-lg shadow-soft">
        <h3 className="text-xl font-heading font-semibold text-teal-900 mb-6">New Deal</h3>

        {error && <p className="text-sm text-feedback-danger mb-4">{error}</p>}

        <div className="space-y-4">
          <div>
            <label className="text-sm font-ui text-text-secondary mb-1 block">Tenant</label>
            <select
              className="input-field"
              value={form.tenant_id}
              onChange={(e) => setForm({ ...form, tenant_id: e.target.value })}
            >
              <option value="">Select tenant...</option>
              {(tenants || []).map((t: any) => (
                <option key={t.id} value={t.id}>{t.full_name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-sm font-ui text-text-secondary mb-1 block">Unit</label>
            <select
              className="input-field"
              value={form.unit_id}
              onChange={(e) => setForm({ ...form, unit_id: e.target.value })}
            >
              <option value="">Select unit...</option>
              {(units || []).map((u: any) => (
                <option key={u.id} value={u.id}>{u.unit_code} ({u.unit_type})</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-sm font-ui text-text-secondary mb-1 block">Term Type</label>
            <select
              className="input-field"
              value={form.term_type}
              onChange={(e) => setForm({ ...form, term_type: e.target.value })}
            >
              <option value="DAILY">Daily</option>
              <option value="MONTHLY">Monthly</option>
              <option value="SIX_MONTHS">6 Months</option>
              <option value="TWELVE_MONTHS">12 Months</option>
            </select>
          </div>
          <div>
            <label className="text-sm font-ui text-text-secondary mb-1 block">Start Date</label>
            <input
              type="date"
              className="input-field"
              value={form.start_date}
              onChange={(e) => setForm({ ...form, start_date: e.target.value })}
            />
          </div>

          {/* Auto-calculated price display */}
          <div className="p-4 rounded-input bg-teal-900/5 border border-teal-900/10">
            <p className="text-xs font-ui text-text-muted mb-1">Unit Price ({form.term_type.replace(/_/g, " ")})</p>
            {autoPrice !== null ? (
              <p className="text-lg font-heading font-semibold text-teal-900">
                {formatCurrency(autoPrice, selectedUnit?.currency || "IDR")}
              </p>
            ) : form.unit_id ? (
              <p className="text-sm text-feedback-warning">No price configured for this term type</p>
            ) : (
              <p className="text-sm text-text-muted">Select a unit to see pricing</p>
            )}
          </div>
        </div>

        <div className="flex gap-3 mt-8 justify-end">
          <button className="btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn-primary" onClick={handleSubmit} disabled={saving}>
            {saving ? "Creating..." : "Create Deal"}
          </button>
        </div>
      </div>
    </div>
  );
}
