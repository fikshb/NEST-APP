"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchUnits, createUnit, updateUnit } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";
import { Plus, Pencil } from "lucide-react";

const STATUS_STYLES: Record<string, string> = {
  AVAILABLE: "badge badge-success",
  RESERVED: "badge badge-warning",
  OCCUPIED: "badge badge-info",
};

export default function UnitsPage() {
  const queryClient = useQueryClient();
  const { data: units, isLoading } = useQuery({
    queryKey: ["units"],
    queryFn: () => fetchUnits(),
  });
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<any>(null);

  const handleSave = async (data: any) => {
    if (editing) {
      await updateUnit(editing.id, data);
    } else {
      await createUnit(data);
    }
    queryClient.invalidateQueries({ queryKey: ["units"] });
    setShowForm(false);
    setEditing(null);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-[28px]">Units</h2>
        <button
          className="btn-primary gap-2"
          onClick={() => {
            setEditing(null);
            setShowForm(true);
          }}
        >
          <Plus size={16} /> Add Unit
        </button>
      </div>

      {showForm && (
        <UnitForm
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
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {(units || []).map((unit: any) => (
            <div key={unit.id} className="card">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <p className="font-ui font-semibold text-teal-900 text-lg">{unit.unit_code}</p>
                  <p className="text-sm text-text-secondary">{unit.unit_type}</p>
                </div>
                <span className={STATUS_STYLES[unit.status] || "badge"}>
                  {unit.status}
                </span>
              </div>
              <div className="space-y-1 text-sm text-text-secondary">
                {unit.daily_price && <p>Daily: {formatCurrency(Number(unit.daily_price), unit.currency)}</p>}
                {unit.monthly_price && <p>Monthly: {formatCurrency(Number(unit.monthly_price), unit.currency)}</p>}
                {unit.six_month_price && <p>6 Months: {formatCurrency(Number(unit.six_month_price), unit.currency)}</p>}
                {unit.twelve_month_price && <p>12 Months: {formatCurrency(Number(unit.twelve_month_price), unit.currency)}</p>}
              </div>
              <button
                className="mt-4 text-xs text-teal-800 hover:underline font-ui flex items-center gap-1"
                onClick={() => {
                  setEditing(unit);
                  setShowForm(true);
                }}
              >
                <Pencil size={12} /> Edit
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function UnitForm({
  initial,
  onSave,
  onCancel,
}: {
  initial: any;
  onSave: (data: any) => Promise<void>;
  onCancel: () => void;
}) {
  const [form, setForm] = useState({
    unit_code: initial?.unit_code || "",
    unit_type: initial?.unit_type || "Standard",
    notes: initial?.notes || "",
    daily_price: initial?.daily_price?.toString() || "",
    monthly_price: initial?.monthly_price?.toString() || "",
    six_month_price: initial?.six_month_price?.toString() || "",
    twelve_month_price: initial?.twelve_month_price?.toString() || "",
  });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async () => {
    if (!form.unit_code) return;
    setSaving(true);
    await onSave({
      ...form,
      daily_price: form.daily_price ? Number(form.daily_price) : null,
      monthly_price: form.monthly_price ? Number(form.monthly_price) : null,
      six_month_price: form.six_month_price ? Number(form.six_month_price) : null,
      twelve_month_price: form.twelve_month_price ? Number(form.twelve_month_price) : null,
    });
    setSaving(false);
  };

  return (
    <div className="card mb-6">
      <h4 className="text-lg font-heading font-semibold text-teal-900 mb-4">
        {initial ? "Edit Unit" : "New Unit"}
      </h4>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="text-sm font-ui text-text-secondary mb-1 block">Unit Code</label>
          <input className="input-field" value={form.unit_code} onChange={(e) => setForm({ ...form, unit_code: e.target.value })} />
        </div>
        <div>
          <label className="text-sm font-ui text-text-secondary mb-1 block">Type</label>
          <select className="input-field" value={form.unit_type} onChange={(e) => setForm({ ...form, unit_type: e.target.value })}>
            <option>Standard</option>
            <option>Deluxe</option>
            <option>Suite</option>
          </select>
        </div>
        <div>
          <label className="text-sm font-ui text-text-secondary mb-1 block">Daily Price</label>
          <input type="number" className="input-field" value={form.daily_price} onChange={(e) => setForm({ ...form, daily_price: e.target.value })} />
        </div>
        <div>
          <label className="text-sm font-ui text-text-secondary mb-1 block">Monthly Price</label>
          <input type="number" className="input-field" value={form.monthly_price} onChange={(e) => setForm({ ...form, monthly_price: e.target.value })} />
        </div>
        <div>
          <label className="text-sm font-ui text-text-secondary mb-1 block">6-Month Price</label>
          <input type="number" className="input-field" value={form.six_month_price} onChange={(e) => setForm({ ...form, six_month_price: e.target.value })} />
        </div>
        <div>
          <label className="text-sm font-ui text-text-secondary mb-1 block">12-Month Price</label>
          <input type="number" className="input-field" value={form.twelve_month_price} onChange={(e) => setForm({ ...form, twelve_month_price: e.target.value })} />
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
