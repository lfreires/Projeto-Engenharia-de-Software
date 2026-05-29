import React from "react";
import { Database, Eye, FileCode2, FileSpreadsheet, FileText, LoaderCircle, Trash2 } from "lucide-react";
import { ProjectMaterial, MaterialType } from "@/models/project";

const TYPE_CONFIG: Record<MaterialType, { label: string; color: string; bg: string; border: string; Icon: React.ElementType }> = {
  pdf:        { label: "PDF",       color: "#fca5a5", bg: "rgba(239, 68, 68, 0.15)",   border: "rgba(239, 68, 68, 0.4)",   Icon: FileText },
  document:   { label: "DOCX",      color: "#93c5fd", bg: "rgba(59, 130, 246, 0.15)",  border: "rgba(59, 130, 246, 0.4)",  Icon: FileText },
  text:       { label: "Texto",     color: "#cbd5e1", bg: "rgba(148, 163, 184, 0.15)", border: "rgba(148, 163, 184, 0.4)", Icon: FileText },
  spreadsheet:{ label: "Planilha",  color: "#86efac", bg: "rgba(34, 197, 94, 0.15)",   border: "rgba(34, 197, 94, 0.4)",   Icon: FileSpreadsheet },
  markdown:   { label: "Markdown",  color: "#93c5fd", bg: "rgba(59, 130, 246, 0.15)",  border: "rgba(59, 130, 246, 0.4)",  Icon: FileText },
  sql:        { label: "SQL",       color: "#fcd34d", bg: "rgba(217, 119, 6, 0.18)",   border: "rgba(217, 119, 6, 0.4)",   Icon: Database },
  yaml:       { label: "YAML",      color: "#c4b5fd", bg: "rgba(124, 58, 237, 0.18)",  border: "rgba(124, 58, 237, 0.4)",  Icon: FileCode2 },
  diagram:    { label: "Diagrama",  color: "#67e8f9", bg: "rgba(8, 145, 178, 0.18)",   border: "rgba(8, 145, 178, 0.4)",   Icon: FileText },
};

interface MaterialCardProps {
  material: ProjectMaterial;
  onSelect?: (material: ProjectMaterial) => void;
  isSelected?: boolean;
  onDelete?: (material: ProjectMaterial) => void;
  isDeleting?: boolean;
}

export function MaterialCard({ material, onSelect, isSelected, onDelete, isDeleting }: MaterialCardProps) {
  const config = TYPE_CONFIG[material.type];
  const Icon = config.Icon;

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={() => onSelect?.(material)}
      onKeyDown={(e) => e.key === "Enter" && onSelect?.(material)}
      style={{
        borderRadius: "8px",
        border: isSelected ? `1px solid rgba(99, 102, 241, 0.5)` : "0.5px solid #232733",
        backgroundColor: isSelected ? "rgba(99, 102, 241, 0.12)" : "#14171f",
        padding: "10px 12px",
        cursor: "pointer",
        transition: "all 0.12s",
      }}
      onMouseEnter={(e) => {
        if (!isSelected) (e.currentTarget as HTMLDivElement).style.backgroundColor = "#1a1d25";
      }}
      onMouseLeave={(e) => {
        if (!isSelected) (e.currentTarget as HTMLDivElement).style.backgroundColor = "#14171f";
      }}
    >
      <div className="flex items-start gap-2.5">
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 mt-0.5"
          style={{ backgroundColor: config.bg, border: `0.5px solid ${config.border}` }}
        >
          <Icon size={15} style={{ color: config.color }} />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5 mb-0.5">
            <span
              style={{
                fontSize: "12.5px",
                fontWeight: 600,
                color: "#e6e8ee",
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
                display: "block",
              }}
            >
              {material.filename}
            </span>
          </div>

          <div className="flex items-center gap-1.5 mb-1.5">
            <span
              style={{
                fontSize: "9.5px",
                fontWeight: 600,
                color: config.color,
                backgroundColor: config.bg,
                border: `0.5px solid ${config.border}`,
                borderRadius: "4px",
                padding: "1px 5px",
              }}
            >
              {config.label}
            </span>
            <span style={{ fontSize: "10px", color: "#6b7080" }}>·</span>
            <span style={{ fontSize: "10px", color: "#8b90a5" }}>{material.size}</span>
            <span style={{ fontSize: "10px", color: "#6b7080" }}>·</span>
            <span style={{ fontSize: "10px", color: "#8b90a5" }}>{material.lastUpdated}</span>
          </div>

          <p
            style={{
              fontSize: "11px",
              color: "#a1a6b8",
              lineHeight: "1.5",
              margin: 0,
              display: "-webkit-box",
              WebkitLineClamp: 2,
              WebkitBoxOrient: "vertical",
              overflow: "hidden",
            }}
          >
            {material.description}
          </p>

          {material.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {material.tags.slice(0, 3).map((tag) => (
                <span
                  key={tag}
                  style={{
                    fontSize: "9.5px",
                    color: "#a1a6b8",
                    backgroundColor: "#1a1d25",
                    border: "0.5px solid #232733",
                    borderRadius: "4px",
                    padding: "1px 6px",
                  }}
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>

        <div className="flex items-center gap-1">
          <button
            type="button"
            title="Excluir material"
            aria-label={`Excluir ${material.filename}`}
            disabled={isDeleting}
            onClick={(event) => {
              event.stopPropagation();
              onDelete?.(material);
            }}
            style={{
              border: "none",
              background: "none",
              padding: "2px",
              color: "#6b7080",
              cursor: isDeleting ? "wait" : "pointer",
            }}
          >
            {isDeleting ? <LoaderCircle size={13} /> : <Trash2 size={13} />}
          </button>
          <Eye size={13} style={{ color: "#6b7080", flexShrink: 0 }} />
        </div>
      </div>
    </div>
  );
}
