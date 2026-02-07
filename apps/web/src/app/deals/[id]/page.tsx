"use client";

import { useState, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import {
  fetchDeal,
  fetchDealJourney,
  fetchDocuments,
  dealGenerateDocument,
  dealRequestInvoice,
  dealUploadInvoice,
  dealClose,
  dealCancel,
  dealEmergencyOverride,
} from "@/lib/api";
import { formatCurrency, formatDate, cn } from "@/lib/utils";
import { CheckCircle2, Circle, AlertCircle, Upload, ChevronLeft } from "lucide-react";

const STEP_ACTIONS: Record<string, { label: string; type: "generate" | "invoice" | "upload" | "close" }> = {
  GENERATE_BOOKING_CONFIRMATION: { label: "Generate Booking Confirmation", type: "generate" },
  GENERATE_LOO_DRAFT: { label: "Generate Offer (LOO Draft)", type: "generate" },
  FINALIZE_LOO: { label: "Finalize Offer (LOO Final)", type: "generate" },
  GENERATE_LEASE_AGREEMENT: { label: "Generate Lease Agreement", type: "generate" },
  GENERATE_OFFICIAL_CONFIRMATION: { label: "Generate Official Confirmation", type: "generate" },
  REQUEST_INVOICE: { label: "Request Invoice", type: "invoice" },
  UPLOAD_INVOICE: { label: "Upload Invoice", type: "upload" },
  GENERATE_MOVE_IN: { label: "Generate Move-in Confirmation", type: "generate" },
  GENERATE_HANDOVER: { label: "Generate Handover Certificate", type: "generate" },
  DEAL_CLOSED: { label: "Close Deal", type: "close" },
};

export default function DealDetailPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const dealId = params.id as string;
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { data: deal, isLoading: dealLoading } = useQuery({
    queryKey: ["deal", dealId],
    queryFn: () => fetchDeal(dealId),
  });

  const { data: journey } = useQuery({
    queryKey: ["journey", dealId],
    queryFn: () => fetchDealJourney(dealId),
  });

  const { data: docs } = useQuery({
    queryKey: ["documents", dealId],
    queryFn: () => fetchDocuments(dealId),
  });

  const [actionLoading, setActionLoading] = useState(false);
  const [showCancel, setShowCancel] = useState(false);
  const [showOverride, setShowOverride] = useState(false);
  const [cancelReason, setCancelReason] = useState("");
  const [overrideReason, setOverrideReason] = useState("");
  const [overrideStep, setOverrideStep] = useState("");

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["deal", dealId] });
    queryClient.invalidateQueries({ queryKey: ["journey", dealId] });
    queryClient.invalidateQueries({ queryKey: ["documents", dealId] });
  };

  const handleAction = async (type: string) => {
    setActionLoading(true);
    try {
      if (type === "generate") {
        await dealGenerateDocument(dealId);
      } else if (type === "invoice") {
        await dealRequestInvoice(dealId);
      } else if (type === "close") {
        await dealClose(dealId);
      }
      invalidate();
    } catch (e: any) {
      alert(e.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setActionLoading(true);
    try {
      await dealUploadInvoice(dealId, file);
      invalidate();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleCancel = async () => {
    if (!cancelReason.trim()) return;
    setActionLoading(true);
    try {
      await dealCancel(dealId, cancelReason);
      setShowCancel(false);
      invalidate();
    } catch (e: any) {
      alert(e.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleOverride = async () => {
    if (!overrideReason.trim() || !overrideStep) return;
    setActionLoading(true);
    try {
      await dealEmergencyOverride(dealId, overrideReason, overrideStep);
      setShowOverride(false);
      invalidate();
    } catch (e: any) {
      alert(e.message);
    } finally {
      setActionLoading(false);
    }
  };

  if (dealLoading) {
    return <p className="text-text-muted font-ui py-12 text-center">Loading deal...</p>;
  }

  if (!deal) {
    return <p className="text-text-muted font-ui py-12 text-center">Deal not found.</p>;
  }

  const isCancelled = deal.status === "CANCELLED";
  const isCompleted = deal.status === "COMPLETED";
  const currentStep = deal.current_step;
  const stepAction = STEP_ACTIONS[currentStep];

  return (
    <div>
      {/* Header */}
      <button
        onClick={() => router.push("/deals")}
        className="flex items-center gap-1 text-sm font-ui text-text-secondary hover:text-teal-900 mb-4"
      >
        <ChevronLeft size={16} /> Back to Deals
      </button>

      <div className="flex items-start justify-between mb-8">
        <div>
          <h2 className="text-[28px]">{deal.deal_code}</h2>
          <p className="text-sm text-text-secondary font-ui mt-1">
            {deal.term_type.replace(/_/g, " ")} — Created {formatDate(deal.created_at)}
          </p>
        </div>
        <div className="flex gap-2">
          {!isCancelled && !isCompleted && (
            <>
              <button className="btn-secondary text-xs" onClick={() => setShowOverride(true)}>
                Emergency Override
              </button>
              <button
                className="text-xs px-4 py-2 rounded-button border border-feedback-danger/30 text-feedback-danger hover:bg-feedback-danger/5 font-ui"
                onClick={() => setShowCancel(true)}
              >
                Cancel Deal
              </button>
            </>
          )}
        </div>
      </div>

      {/* Cancelled banner */}
      {isCancelled && (
        <div className="card border-feedback-danger/30 bg-feedback-danger/5 mb-6">
          <p className="font-ui font-medium text-feedback-danger text-sm">
            This deal has been cancelled.
          </p>
          {deal.cancellation_reason && (
            <p className="text-sm text-text-secondary mt-1">Reason: {deal.cancellation_reason}</p>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Tenant & Unit Summary + Journey */}
        <div className="lg:col-span-2 space-y-6">
          {/* Tenant & Unit summary */}
          <div className="card">
            <div className="grid grid-cols-2 gap-6">
              <div>
                <p className="text-xs font-ui text-text-muted mb-1">Tenant</p>
                <p className="font-ui font-medium text-teal-900">{deal.tenant?.full_name}</p>
                <p className="text-sm text-text-secondary">{deal.tenant?.email}</p>
                <p className="text-sm text-text-secondary">{deal.tenant?.phone}</p>
              </div>
              <div>
                <p className="text-xs font-ui text-text-muted mb-1">Unit</p>
                <p className="font-ui font-medium text-teal-900">
                  {deal.unit?.unit_code} ({deal.unit?.unit_type})
                </p>
                <p className="text-sm text-text-secondary">
                  {formatCurrency(Number(deal.deal_price), deal.currency)}
                </p>
              </div>
            </div>
          </div>

          {/* Journey Checklist */}
          <div className="card">
            <h4 className="text-lg font-heading font-semibold text-teal-900 mb-6">
              Journey Progress
            </h4>
            <div className="space-y-1">
              {(journey?.steps || []).map((step: any, i: number) => (
                <div
                  key={step.step}
                  className={cn(
                    "flex items-start gap-3 p-3 rounded-input transition-colors",
                    step.status === "current" && "bg-teal-900/5 border border-teal-900/10",
                    step.status === "completed" && "opacity-70"
                  )}
                >
                  {step.status === "completed" ? (
                    <CheckCircle2 size={20} className="text-feedback-success mt-0.5 shrink-0" />
                  ) : step.status === "current" ? (
                    <AlertCircle size={20} className="text-teal-900 mt-0.5 shrink-0" />
                  ) : (
                    <Circle size={20} className="text-text-muted mt-0.5 shrink-0" />
                  )}
                  <div className="flex-1">
                    <p
                      className={cn(
                        "text-sm font-ui",
                        step.status === "current"
                          ? "font-medium text-teal-900"
                          : step.status === "completed"
                          ? "text-text-secondary line-through"
                          : "text-text-muted"
                      )}
                    >
                      {step.label}
                    </p>
                    {step.status === "current" && step.blocked_reason && (
                      <p className="text-xs text-feedback-warning mt-1">{step.blocked_reason}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Primary Action Button */}
            {!isCancelled && !isCompleted && stepAction && (
              <div className="mt-6 pt-6 border-t border-line-soft">
                {stepAction.type === "upload" ? (
                  <div>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".pdf,.jpg,.jpeg,.png"
                      className="hidden"
                      onChange={handleUpload}
                    />
                    <button
                      className="btn-primary gap-2 w-full"
                      onClick={() => fileInputRef.current?.click()}
                      disabled={actionLoading}
                    >
                      <Upload size={16} />
                      {actionLoading ? "Uploading..." : stepAction.label}
                    </button>
                  </div>
                ) : (
                  <button
                    className="btn-primary w-full"
                    onClick={() => handleAction(stepAction.type)}
                    disabled={actionLoading}
                  >
                    {actionLoading ? "Processing..." : stepAction.label}
                  </button>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right: Documents */}
        <div className="space-y-6">
          <div className="card">
            <h4 className="text-lg font-heading font-semibold text-teal-900 mb-4">
              Documents
            </h4>
            {(docs || []).length === 0 ? (
              <p className="text-sm text-text-muted font-ui">No documents yet.</p>
            ) : (
              <div className="space-y-3">
                {(docs || []).map((doc: any) => (
                  <div key={doc.id} className="p-3 rounded-input border border-line-soft">
                    <p className="text-sm font-ui font-medium text-teal-900">
                      {doc.doc_type.replace(/_/g, " ")}
                    </p>
                    <p className="text-xs text-text-muted mt-1">
                      Version {doc.latest_version}
                    </p>
                    {doc.versions?.[0] && (
                      <div className="flex gap-2 mt-2">
                        <a
                          href={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/documents/${doc.id}/versions/${doc.versions[0].id}/preview`}
                          target="_blank"
                          className="text-xs text-teal-800 hover:underline font-ui"
                        >
                          Preview
                        </a>
                        <a
                          href={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/documents/${doc.id}/versions/${doc.versions[0].id}/pdf`}
                          target="_blank"
                          className="text-xs text-teal-800 hover:underline font-ui"
                        >
                          Download PDF
                        </a>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Cancel Modal */}
      {showCancel && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-modal p-8 w-full max-w-md shadow-soft">
            <h3 className="text-xl font-heading font-semibold text-teal-900 mb-4">Cancel Deal</h3>
            <p className="text-sm text-text-secondary mb-4">
              This action cannot be undone. The deal will become read-only and the unit will be released.
            </p>
            <textarea
              className="input-field"
              rows={3}
              placeholder="Reason for cancellation (required)"
              value={cancelReason}
              onChange={(e) => setCancelReason(e.target.value)}
            />
            <div className="flex gap-3 mt-6 justify-end">
              <button className="btn-secondary" onClick={() => setShowCancel(false)}>Back</button>
              <button
                className="text-sm px-6 py-3 rounded-button bg-feedback-danger text-white font-ui"
                onClick={handleCancel}
                disabled={actionLoading || !cancelReason.trim()}
              >
                Confirm Cancellation
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Override Modal */}
      {showOverride && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-modal p-8 w-full max-w-md shadow-soft">
            <h3 className="text-xl font-heading font-semibold text-teal-900 mb-4">Emergency Override</h3>
            <p className="text-sm text-text-secondary mb-4">
              This bypasses the journey sequence. A reason is mandatory and the action will be fully audited.
            </p>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-ui text-text-secondary mb-1 block">Target Step</label>
                <select
                  className="input-field"
                  value={overrideStep}
                  onChange={(e) => setOverrideStep(e.target.value)}
                >
                  <option value="">Select step...</option>
                  {(journey?.steps || []).map((s: any) => (
                    <option key={s.step} value={s.step}>{s.label}</option>
                  ))}
                </select>
              </div>
              <textarea
                className="input-field"
                rows={3}
                placeholder="Reason for override (required)"
                value={overrideReason}
                onChange={(e) => setOverrideReason(e.target.value)}
              />
            </div>
            <div className="flex gap-3 mt-6 justify-end">
              <button className="btn-secondary" onClick={() => setShowOverride(false)}>Back</button>
              <button
                className="btn-primary"
                onClick={handleOverride}
                disabled={actionLoading || !overrideReason.trim() || !overrideStep}
              >
                Apply Override
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
