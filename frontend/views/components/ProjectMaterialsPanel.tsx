import React from "react";
import { X, FolderOpen, Search } from "lucide-react";
import { ProjectMaterial } from "@/models/project";
import { MaterialCard } from "./MaterialCard";

interface ProjectMaterialsPanelProps {
  materials: ProjectMaterial[];
  selectedMaterial: ProjectMaterial | null;
  onSelectMaterial: (material: ProjectMaterial) => void;
  onClose: () => void;
}

export function ProjectMaterialsPanel({
  materials,
  selectedMaterial,
  onSelectMaterial,
  onClose,
}: ProjectMaterialsPanelProps) {
  const [filter, setFilter] = React.useState("");

  const filtered = filter.trim()
    ? materials.filter(
        (m) =>
          m.filename.toLowerCase().includes(filter.toLowerCase()) ||
          m.label.toLowerCase().includes(filter.toLowerCase()) ||
          m.tags.some((t) => t.toLowerCase().includes(filter.toLowerCase()))
      )
    : materials;

  return (
    <div
      className="flex flex-col h-full shrink-0"
      style={{ width: "280px", borderLeft: "0.5px solid #e2e5ee", backgroundColor: "#ffffff" }}
    >
      {/* Header */}
      <div
        className="shrink-0 flex items-center gap-2 px-4"
        style={{ height: "60px", borderBottom: "0.5px solid #e2e5ee" }}
      >
        <div
          className="w-6 h-6 rounded-md flex items-center justify-center"
          style={{ backgroundColor: "#eef2ff" }}
        >
          <FolderOpen size={13} style={{ color: "#4f46e5" }} />
        </div>

        <div className="flex-1">
          <p style={{ fontSize: "13px", fontWeight: 600, color: "#111827", margin: 0 }}>
            Materiais
          </p>
          <p style={{ fontSize: "10.5px", color: "#a0a4b8", margin: 0 }}>
            {materials.length} documentos indexados
          </p>
        </div>

        <button
          onClick={onClose}
          className="w-6 h-6 rounded-md flex items-center justify-center"
          style={{ color: "#c0c4d6", background: "none", border: "none", cursor: "pointer" }}
          title="Fechar painel"
        >
          <X size={14} />
        </button>
      </div>

      {/* Search */}
      <div className="px-4 py-3" style={{ borderBottom: "0.5px solid #f0f1f8" }}>
        <div
          className="flex items-center gap-2"
          style={{
            borderRadius: "7px",
            border: "0.5px solid #e0e3ef",
            backgroundColor: "#f8f9fc",
            padding: "6px 10px",
          }}
        >
          <Search size={12} style={{ color: "#a0a4b8", flexShrink: 0 }} />
          <input
            type="text"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Filtrar materiais..."
            style={{
              fontSize: "12.5px",
              color: "#1e2035",
              backgroundColor: "transparent",
              border: "none",
              outline: "none",
              flex: 1,
              minWidth: 0,
            }}
          />
        </div>
      </div>

      {/* List */}
      <div
        className="flex-1 overflow-y-auto"
        style={{ padding: "10px 12px", display: "flex", flexDirection: "column", gap: "6px" }}
      >
        {filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-10 text-center">
            <FolderOpen size={28} style={{ color: "#d0d4e8", marginBottom: "8px" }} />
            <p style={{ fontSize: "12px", color: "#a0a4b8" }}>Nenhum material encontrado</p>
          </div>
        ) : (
          filtered.map((m) => (
            <MaterialCard
              key={m.id}
              material={m}
              onSelect={onSelectMaterial}
              isSelected={selectedMaterial?.id === m.id}
            />
          ))
        )}
      </div>

      {/* Footer */}
      <div
        className="shrink-0 px-4 py-2.5"
        style={{ borderTop: "0.5px solid #e5e8f0", backgroundColor: "#f8f9fc" }}
      >
        <p style={{ fontSize: "10.5px", color: "#b0b5c8", margin: 0, textAlign: "center" }}>
          Clique num material para visualizá-lo no chat
        </p>
      </div>
    </div>
  );
}
