"use client";

import { useState, useRef } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchStaticDocuments, uploadStaticDocument } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { formatDate } from "@/lib/utils";
import { Upload, FileText, ExternalLink } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function DocumentLibraryPage() {
  const queryClient = useQueryClient();
  const { data: staticDocs, isLoading } = useQuery({
    queryKey: ["static-documents"],
    queryFn: fetchStaticDocuments,
  });

  const catalogFileRef = useRef<HTMLInputElement>(null);
  const pricelistFileRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState<string | null>(null);

  const handleUpload = async (docType: string, file: File) => {
    setUploading(docType);
    try {
      await uploadStaticDocument(docType, file);
      queryClient.invalidateQueries({ queryKey: ["static-documents"] });
    } catch (e: any) {
      alert(e.message);
    } finally {
      setUploading(null);
    }
  };

  const catalog = (staticDocs || []).find((d: any) => d.doc_type === "CATALOG");
  const pricelist = (staticDocs || []).find((d: any) => d.doc_type === "PRICELIST");

  return (
    <div>
      <h2 className="text-[28px] mb-8">Document Library</h2>

      {isLoading ? (
        <p className="text-text-muted font-ui">Loading...</p>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Catalog */}
          <DocCard
            title="Unit Catalog"
            doc={catalog}
            docType="CATALOG"
            uploading={uploading === "CATALOG"}
            fileRef={catalogFileRef}
            onUpload={(file) => handleUpload("CATALOG", file)}
          />

          {/* Pricelist */}
          <DocCard
            title="Pricelist"
            doc={pricelist}
            docType="PRICELIST"
            uploading={uploading === "PRICELIST"}
            fileRef={pricelistFileRef}
            onUpload={(file) => handleUpload("PRICELIST", file)}
          />
        </div>
      )}
    </div>
  );
}

function DocCard({
  title,
  doc,
  docType,
  uploading,
  fileRef,
  onUpload,
}: {
  title: string;
  doc: any;
  docType: string;
  uploading: boolean;
  fileRef: React.RefObject<HTMLInputElement>;
  onUpload: (file: File) => void;
}) {
  const activeVersion = doc?.versions?.find((v: any) => v.is_active);

  return (
    <div className="card">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <FileText size={24} className="text-teal-900" />
          <h4 className="text-lg font-heading font-semibold text-teal-900">{title}</h4>
        </div>
        <div>
          <input
            ref={fileRef}
            type="file"
            accept=".pdf"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) onUpload(f);
            }}
          />
          <button
            className="btn-secondary text-xs gap-1"
            onClick={() => fileRef.current?.click()}
            disabled={uploading}
          >
            <Upload size={14} />
            {uploading ? "Uploading..." : "Upload New Version"}
          </button>
        </div>
      </div>

      {activeVersion ? (
        <div className="p-4 rounded-input border border-line-soft bg-neutral-softWhite">
          <p className="text-sm font-ui font-medium text-teal-900">
            {activeVersion.file_name}
          </p>
          <p className="text-xs text-text-muted mt-1">
            Version {activeVersion.version_no} — Uploaded {formatDate(activeVersion.uploaded_at)}
          </p>
          {activeVersion.notes && (
            <p className="text-xs text-text-secondary mt-1">{activeVersion.notes}</p>
          )}
          <a
            href={`${API_BASE}/static-documents/${docType}/active?token=${getToken() || ""}`}
            target="_blank"
            className="inline-flex items-center gap-1 mt-3 text-xs text-teal-800 hover:underline font-ui"
          >
            <ExternalLink size={12} /> View Active PDF
          </a>
        </div>
      ) : (
        <p className="text-sm text-text-muted font-ui">No active version.</p>
      )}

      {doc?.versions && doc.versions.length > 1 && (
        <div className="mt-4">
          <p className="text-xs font-ui text-text-muted mb-2">All Versions ({doc.versions.length})</p>
          <div className="space-y-2">
            {doc.versions.map((v: any) => (
              <div key={v.id} className="flex items-center justify-between text-xs text-text-secondary">
                <span>
                  v{v.version_no} — {v.file_name}
                  {v.is_active && <span className="ml-2 badge text-[10px]">Active</span>}
                </span>
                <span>{formatDate(v.uploaded_at)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
