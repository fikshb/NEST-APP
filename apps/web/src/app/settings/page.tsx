"use client";

import { useState, useEffect, useRef } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchSettings, updateSettings } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Upload } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function SettingsPage() {
  const queryClient = useQueryClient();
  const { data: settings, isLoading } = useQuery({
    queryKey: ["settings"],
    queryFn: fetchSettings,
  });

  const [form, setForm] = useState({
    company_legal_name: "",
    company_address: "",
    signatory_name: "",
    signatory_title: "",
    finance_email: "",
    bot_whatsapp_number: "",
  });
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const logoRef = useRef<HTMLInputElement>(null);
  const sigRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (settings) {
      setForm({
        company_legal_name: settings.company_legal_name || "",
        company_address: settings.company_address || "",
        signatory_name: settings.signatory_name || "",
        signatory_title: settings.signatory_title || "",
        finance_email: settings.finance_email || "",
        bot_whatsapp_number: settings.bot_whatsapp_number || "",
      });
    }
  }, [settings]);

  const handleSave = async () => {
    setSaving(true);
    setMessage("");
    try {
      await updateSettings(form);
      queryClient.invalidateQueries({ queryKey: ["settings"] });
      setMessage("Settings saved successfully.");
    } catch (e: any) {
      setMessage(e.message);
    } finally {
      setSaving(false);
    }
  };

  const handleFileUpload = async (type: "logo" | "signature", file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch(`${API_BASE}/settings/${type}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${getToken()}` },
        body: formData,
      });
      if (!res.ok) throw new Error(await res.text());
      queryClient.invalidateQueries({ queryKey: ["settings"] });
      setMessage(`${type === "logo" ? "Logo" : "Signature"} uploaded.`);
    } catch {
      setMessage("Upload failed.");
    }
  };

  if (isLoading) {
    return <p className="text-text-muted font-ui py-12 text-center">Loading settings...</p>;
  }

  return (
    <div>
      <h2 className="text-[28px] mb-8">Settings</h2>

      <div className="max-w-2xl space-y-6">
        {/* Company Info */}
        <div className="card">
          <h4 className="text-lg font-heading font-semibold text-teal-900 mb-4">
            Company Information
          </h4>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-ui text-text-secondary mb-1 block">Legal Name</label>
              <input
                className="input-field"
                value={form.company_legal_name}
                onChange={(e) => setForm({ ...form, company_legal_name: e.target.value })}
              />
            </div>
            <div>
              <label className="text-sm font-ui text-text-secondary mb-1 block">Address</label>
              <textarea
                className="input-field"
                rows={2}
                value={form.company_address}
                onChange={(e) => setForm({ ...form, company_address: e.target.value })}
              />
            </div>
          </div>
        </div>

        {/* Logo & Signature */}
        <div className="card">
          <h4 className="text-lg font-heading font-semibold text-teal-900 mb-4">
            Logo &amp; Signature
          </h4>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <p className="text-sm font-ui text-text-secondary mb-2">Company Logo</p>
              {settings?.logo_path && (
                <p className="text-xs text-text-muted mb-2">Current: {settings.logo_path}</p>
              )}
              <input
                ref={logoRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => {
                  const f = e.target.files?.[0];
                  if (f) handleFileUpload("logo", f);
                }}
              />
              <button className="btn-secondary text-xs gap-1" onClick={() => logoRef.current?.click()}>
                <Upload size={14} /> Upload Logo
              </button>
            </div>
            <div>
              <p className="text-sm font-ui text-text-secondary mb-2">Signature Image</p>
              {settings?.signature_image_path && (
                <p className="text-xs text-text-muted mb-2">Current: {settings.signature_image_path}</p>
              )}
              <input
                ref={sigRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => {
                  const f = e.target.files?.[0];
                  if (f) handleFileUpload("signature", f);
                }}
              />
              <button className="btn-secondary text-xs gap-1" onClick={() => sigRef.current?.click()}>
                <Upload size={14} /> Upload Signature
              </button>
            </div>
          </div>
        </div>

        {/* Signatory */}
        <div className="card">
          <h4 className="text-lg font-heading font-semibold text-teal-900 mb-4">
            Authorized Signatory
          </h4>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-ui text-text-secondary mb-1 block">Name</label>
              <input
                className="input-field"
                value={form.signatory_name}
                onChange={(e) => setForm({ ...form, signatory_name: e.target.value })}
              />
            </div>
            <div>
              <label className="text-sm font-ui text-text-secondary mb-1 block">Title</label>
              <input
                className="input-field"
                value={form.signatory_title}
                onChange={(e) => setForm({ ...form, signatory_title: e.target.value })}
              />
            </div>
          </div>
        </div>

        {/* Finance & Bot */}
        <div className="card">
          <h4 className="text-lg font-heading font-semibold text-teal-900 mb-4">
            Finance &amp; Bot
          </h4>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-ui text-text-secondary mb-1 block">Finance Email</label>
              <input
                type="email"
                className="input-field"
                value={form.finance_email}
                onChange={(e) => setForm({ ...form, finance_email: e.target.value })}
              />
            </div>
            <div>
              <label className="text-sm font-ui text-text-secondary mb-1 block">Bot WhatsApp Number</label>
              <input
                className="input-field"
                value={form.bot_whatsapp_number}
                onChange={(e) => setForm({ ...form, bot_whatsapp_number: e.target.value })}
              />
            </div>
          </div>
        </div>

        {/* Save */}
        {message && (
          <p className="text-sm font-ui text-feedback-success">{message}</p>
        )}
        <div className="flex justify-end">
          <button className="btn-primary" onClick={handleSave} disabled={saving}>
            {saving ? "Saving..." : "Save Settings"}
          </button>
        </div>
      </div>
    </div>
  );
}
