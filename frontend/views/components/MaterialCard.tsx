import React from "react";
import { FileText, FileSpreadsheet, FileCode2, Database, Eye } from "lucide-react";
import { ProjectMaterial, MaterialType } from "@/models/project";

const TYPE_CONFIG: Record<MaterialType, { label: string; color: string; bg: string; border: string; Icon: React.ElementType }> = {
  pdf:        { label: "PDF",       color: "#dc2626", bg: "#fef2f2", border: "#fecaca", Icon: FileText },
  spreadsheet:{ label: "Planilha",  color: "#16a34a", bg: "#f0fdf4", border: "#bbf7d0", Icon: FileSpreadsheet },
  markdown:   { label: "Markdown",  color: "#2563eb", bg: "#eff6ff", border: "#bfdbfe", Icon: FileText },
  sql:        { label: "SQL",       color: "#d97706", bg: "#fffbeb", border: "#fde68a", Icon: Database },
  yaml:       { label: "YAML",      color: "#7c3aed", bg: "#f5f3ff", border: "#ddd6fe", Icon: FileCode2 },
  diagram:    { label: "Diagrama",  color: "#0891b2", bg: "#ecfeff", border: "#a5f3fc", Icon: FileText },
};

interface MaterialCardProps {
  material: ProjectMaterial;
  onSelect?: (material: ProjectMaterial) => void;
  isSelected?: boolean;
}

export function MaterialCard({ material, onSelect, isSelected }: MaterialCardProps) {
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
        border: isSelected ? `1px solid #a5b4fc` : "0.5px solid #e5e8f0",
        backgroundColor: isSelected ? "#f5f3ff" : "#ffffff",
        padding: "10px 12px",
        cursor: "pointer",
        transition: "all 0.12s",
      }}
      onMouseEnter={(e) => {
        if (!isSelected) (e.currentTarget as HTMLDivElement).style.backgroundColor = "#f8f9ff";
      }}
      onMouseLeave={(e) => {
        if (!isSelected) (e.currentTarget as HTMLDivElement).style.backgroundColor = "#ffffff";
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
                color: "#1e2035",
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
            <span style={{ fontSize: "10px", color: "#a0a4b8" }}>·</span>
            <span style={{ fontSize: "10px", color: "#a0a4b8" }}>{material.size}</span>
            <span style={{ fontSize: "10px", color: "#a0a4b8" }}>·</span>
            <span style={{ fontSize: "10px", color: "#a0a4b8" }}>{material.lastUpdated}</span>
          </div>

          <p
            style={{
              fontSize: "11px",
              color: "#6b7080",
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
                    color: "#7c80a0",
                    backgroundColor: "#f0f1f8",
                    border: "0.5px solid #e0e3ef",
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

        <Eye
          size={13}
          style={{ color: "#c0c4d6", flexShrink: 0, marginTop: "2px" }}
        />
      </div>
    </div>
  );
}
