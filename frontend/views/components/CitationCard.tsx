import React from "react";
import { FileText, FileSpreadsheet, FileCode2, Database, ExternalLink } from "lucide-react";
import { CitationSource } from "@/models/citation";
import { MaterialType } from "@/models/project";

const TYPE_CONFIG: Record<MaterialType, { label: string; color: string; bg: string; border: string; Icon: React.ElementType }> = {
  pdf:        { label: "PDF",        color: "#dc2626", bg: "#fef2f2", border: "#fecaca", Icon: FileText },
  spreadsheet:{ label: "Planilha",   color: "#16a34a", bg: "#f0fdf4", border: "#bbf7d0", Icon: FileSpreadsheet },
  markdown:   { label: "Markdown",   color: "#2563eb", bg: "#eff6ff", border: "#bfdbfe", Icon: FileText },
  sql:        { label: "SQL",        color: "#d97706", bg: "#fffbeb", border: "#fde68a", Icon: Database },
  yaml:       { label: "YAML",       color: "#7c3aed", bg: "#f5f3ff", border: "#ddd6fe", Icon: FileCode2 },
  diagram:    { label: "Diagrama",   color: "#0891b2", bg: "#ecfeff", border: "#a5f3fc", Icon: FileText },
};

interface CitationCardProps {
  citation: CitationSource;
  onViewMaterial?: (materialId: string) => void;
}

export function CitationCard({ citation, onViewMaterial }: CitationCardProps) {
  const config = TYPE_CONFIG[citation.type];
  const Icon = config.Icon;

  return (
    <div
      style={{
        borderRadius: "8px",
        border: "0.5px solid #e5e8f0",
        backgroundColor: "#fafbff",
        padding: "10px 12px",
        marginTop: "6px",
      }}
    >
      <div className="flex items-center gap-2 mb-1.5">
        <div
          className="w-5 h-5 rounded flex items-center justify-center shrink-0"
          style={{ backgroundColor: config.bg, border: `0.5px solid ${config.border}` }}
        >
          <Icon size={11} style={{ color: config.color }} />
        </div>

        <span style={{ fontSize: "12px", fontWeight: 600, color: "#1e2035", flex: 1 }}>
          {citation.filename}
        </span>

        <span
          style={{
            fontSize: "9.5px",
            fontWeight: 600,
            color: config.color,
            backgroundColor: config.bg,
            border: `0.5px solid ${config.border}`,
            borderRadius: "4px",
            padding: "1px 6px",
          }}
        >
          {config.label}
        </span>
      </div>

      <p style={{ fontSize: "11.5px", color: "#6b7080", lineHeight: "1.55", margin: 0, marginBottom: onViewMaterial ? "8px" : 0 }}>
        "{citation.excerpt}"
      </p>

      {onViewMaterial && (
        <button
          onClick={() => onViewMaterial(citation.materialId)}
          className="flex items-center gap-1 mt-1"
          style={{ fontSize: "11px", fontWeight: 500, color: "#4f46e5", background: "none", border: "none", padding: 0, cursor: "pointer" }}
        >
          <ExternalLink size={10} />
          Ver material
        </button>
      )}
    </div>
  );
}
