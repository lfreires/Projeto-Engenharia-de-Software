import React from "react";
import { X, FolderOpen, Search } from "lucide-react";
import { ProjectMaterial } from "@/models/project";
import { MaterialCard } from "./MaterialCard";
import { MaterialViewer } from "./MaterialViewer";
import { MaterialUpload } from "./MaterialUpload";

interface ProjectMaterialsPanelProps {
  materials: ProjectMaterial[];
  selectedMaterial: ProjectMaterial | null;
  onSelectMaterial: (material: ProjectMaterial) => void;
  onClearSelection: () => void;
  onUpload: (file: File) => Promise<void>;
  onDelete: (material: ProjectMaterial) => Promise<void>;
  onClose: () => void;
}

export function ProjectMaterialsPanel({
  materials,
  selectedMaterial,
  onSelectMaterial,
  onClearSelection,
  onUpload,
  onDelete,
  onClose,
}: ProjectMaterialsPanelProps) {
  const [filter, setFilter] = React.useState("");
  const [deletingId, setDeletingId] = React.useState<string | null>(null);
  const [deleteError, setDeleteError] = React.useState<string | null>(null);

  async function handleDelete(material: ProjectMaterial) {
    const confirmed = window.confirm(
      `Excluir "${material.filename}"? Ele deixara de ser usado nas respostas do chat.`,
    );
    if (!confirmed) return;
    setDeletingId(material.id);
    setDeleteError(null);
    try {
      await onDelete(material);
    } catch (reason) {
      const message = reason instanceof Error ? reason.message : "Nao foi possivel excluir.";
      setDeleteError(message);
    } finally {
      setDeletingId(null);
    }
  }

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
      style={{ width: "390px", borderLeft: "0.5px solid #232733", backgroundColor: "#11141b" }}
    >
      {/* Header */}
      <div
        className="shrink-0 flex items-center gap-2 px-4"
        style={{ height: "60px", borderBottom: "0.5px solid #232733" }}
      >
        <div
          className="w-6 h-6 rounded-md flex items-center justify-center"
          style={{ backgroundColor: "rgba(99, 102, 241, 0.18)" }}
        >
          <FolderOpen size={13} style={{ color: "#a5b4fc" }} />
        </div>

        <div className="flex-1">
          <p style={{ fontSize: "13px", fontWeight: 600, color: "#f3f4f9", margin: 0 }}>
            Materiais
          </p>
          <p style={{ fontSize: "10.5px", color: "#8b90a5", margin: 0 }}>
            {materials.length} documentos indexados
          </p>
        </div>

        <button
          onClick={onClose}
          className="w-6 h-6 rounded-md flex items-center justify-center"
          style={{ color: "#8b90a5", background: "none", border: "none", cursor: "pointer" }}
          title="Fechar painel"
        >
          <X size={14} />
        </button>
      </div>

      {deleteError && (
        <p
          className="mx-4 mt-3 rounded-md px-3 py-2"
          style={{ fontSize: "11.5px", color: "#fca5a5", backgroundColor: "rgba(239, 68, 68, 0.12)", border: "0.5px solid rgba(239, 68, 68, 0.35)" }}
        >
          Falha ao excluir: {deleteError}
        </p>
      )}

      {selectedMaterial ? (
        <MaterialViewer
          material={selectedMaterial}
          onBack={onClearSelection}
          onDelete={handleDelete}
          isDeleting={deletingId === selectedMaterial.id}
        />
      ) : (
        <>
      <MaterialUpload
        onUpload={onUpload}
        showArchitectureOption={!materials.some((material) => material.filename === "arquitetura-original.md")}
      />
      {/* Search */}
      <div className="px-4 py-3" style={{ borderBottom: "0.5px solid #1f2330" }}>
        <div
          className="flex items-center gap-2"
          style={{
            borderRadius: "7px",
            border: "0.5px solid #232733",
            backgroundColor: "#14171f",
            padding: "6px 10px",
          }}
        >
          <Search size={12} style={{ color: "#6b7080", flexShrink: 0 }} />
          <input
            type="text"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Filtrar materiais..."
            className="placeholder:text-[#6b7080]"
            style={{
              fontSize: "12.5px",
              color: "#e6e8ee",
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
            <FolderOpen size={28} style={{ color: "#3a3f4d", marginBottom: "8px" }} />
            <p style={{ fontSize: "12px", color: "#6b7080" }}>
              Envie um documento para comecar
            </p>
          </div>
        ) : (
          filtered.map((m) => (
            <MaterialCard
              key={m.id}
              material={m}
              onSelect={onSelectMaterial}
              isSelected={selectedMaterial?.id === m.id}
              onDelete={handleDelete}
              isDeleting={deletingId === m.id}
            />
          ))
        )}
      </div>

      {/* Footer */}
      <div
        className="shrink-0 px-4 py-2.5"
        style={{ borderTop: "0.5px solid #232733", backgroundColor: "#0e1117" }}
      >
        <p style={{ fontSize: "10.5px", color: "#6b7080", margin: 0, textAlign: "center" }}>
          Clique num material para abrir o documento
        </p>
      </div>
        </>
      )}
    </div>
  );
}
