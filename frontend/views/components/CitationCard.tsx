import React from "react";
import { FileText, FileSpreadsheet, FileCode2, Database, ExternalLink } from "lucide-react";
import { CitationSource } from "@/models/citation";
import { MaterialType } from "@/models/project";

const TYPE_CONFIG: Record<MaterialType, { label: string; color: string; bg: string; border: string; Icon: React.ElementType }> = {
  pdf:        { label: "PDF",        color: "#fca5a5", bg: "rgba(239, 68, 68, 0.15)",  border: "rgba(239, 68, 68, 0.4)",  Icon: FileText },
  document:   { label: "DOCX",       color: "#93c5fd", bg: "rgba(59, 130, 246, 0.15)", border: "rgba(59, 130, 246, 0.4)", Icon: FileText },
  text:       { label: "Texto",      color: "#cbd5e1", bg: "rgba(148, 163, 184, 0.15)",border: "rgba(148, 163, 184, 0.4)",Icon: FileText },
  spreadsheet:{ label: "Planilha",   color: "#86efac", bg: "rgba(34, 197, 94, 0.15)",  border: "rgba(34, 197, 94, 0.4)",  Icon: FileSpreadsheet },
  markdown:   { label: "Markdown",   color: "#93c5fd", bg: "rgba(59, 130, 246, 0.15)", border: "rgba(59, 130, 246, 0.4)", Icon: FileText },
  sql:        { label: "SQL",        color: "#fcd34d", bg: "rgba(217, 119, 6, 0.18)",  border: "rgba(217, 119, 6, 0.4)",  Icon: Database },
  yaml:       { label: "YAML",       color: "#c4b5fd", bg: "rgba(124, 58, 237, 0.18)", border: "rgba(124, 58, 237, 0.4)", Icon: FileCode2 },
  diagram:    { label: "Diagrama",   color: "#67e8f9", bg: "rgba(8, 145, 178, 0.18)",  border: "rgba(8, 145, 178, 0.4)",  Icon: FileText },
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
        border: "0.5px solid #232733",
        backgroundColor: "#14171f",
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

        <span style={{ fontSize: "12px", fontWeight: 600, color: "#e6e8ee", flex: 1 }}>
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

      {citation.location && (
        <p style={{ fontSize: "10.5px", color: "#a5b4fc", margin: "0 0 6px 0" }}>
          {citation.location}
        </p>
      )}

      <p style={{ fontSize: "11.5px", color: "#a1a6b8", lineHeight: "1.55", margin: 0, marginBottom: onViewMaterial ? "8px" : 0 }}>
        "{citation.excerpt}"
      </p>

      {onViewMaterial && (
        <button
          onClick={() => onViewMaterial(citation.materialId)}
          className="flex items-center gap-1 mt-1"
          style={{ fontSize: "11px", fontWeight: 500, color: "#a5b4fc", background: "none", border: "none", padding: 0, cursor: "pointer" }}
        >
          <ExternalLink size={10} />
          Ver material
        </button>
      )}
    </div>
  );
}
