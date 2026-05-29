import React from "react";
import { FolderOpen, RotateCcw } from "lucide-react";

interface ConsultationHeaderProps {
  projectName: string;
  materialsCount: number;
  showMaterials: boolean;
  onToggleMaterials: () => void;
  onNewChat: () => void;
}

export function ConsultationHeader({
  projectName,
  materialsCount,
  showMaterials,
  onToggleMaterials,
  onNewChat,
}: ConsultationHeaderProps) {
  return (
    <header
      className="shrink-0 flex items-center px-6 gap-3"
      style={{ height: "60px", borderBottom: "0.5px solid #232733", backgroundColor: "#11141b" }}
    >
      {/* Left — title + project */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2.5">
          <h1 style={{ fontSize: "15px", fontWeight: 600, color: "#f3f4f9", margin: 0 }}>
            Consulta ao Projeto
          </h1>

          <span
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full"
            style={{
              fontSize: "10.5px",
              fontWeight: 500,
              backgroundColor: "rgba(34, 197, 94, 0.15)",
              border: "0.5px solid rgba(34, 197, 94, 0.35)",
              color: "#86efac",
            }}
          >
            <span
              className="w-1.5 h-1.5 rounded-full"
              style={{ backgroundColor: "#22c55e", display: "inline-block" }}
            />
            IA Ativa
          </span>
        </div>

        <p style={{ fontSize: "11.5px", color: "#8b90a5", margin: 0, marginTop: "1px" }}>
          Projeto:{" "}
          <span style={{ color: "#a5b4fc", fontWeight: 500 }}>{projectName}</span>
        </p>
      </div>

      {/* Right — action buttons */}
      <div className="flex items-center gap-2 shrink-0">
        <button
          onClick={onNewChat}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors"
          style={{
            fontSize: "12px",
            fontWeight: 500,
            color: "#c4c8d6",
            backgroundColor: "#1a1d25",
            border: "0.5px solid #232733",
            cursor: "pointer",
          }}
          title="Nova consulta"
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#1f2330";
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#1a1d25";
          }}
        >
          <RotateCcw size={12} />
          Nova
        </button>

        <button
          onClick={onToggleMaterials}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors"
          style={{
            fontSize: "12px",
            fontWeight: 500,
            color: showMaterials ? "#a5b4fc" : "#c4c8d6",
            backgroundColor: showMaterials ? "rgba(99, 102, 241, 0.18)" : "#1a1d25",
            border: showMaterials ? "0.5px solid rgba(99, 102, 241, 0.45)" : "0.5px solid #232733",
            cursor: "pointer",
          }}
          title="Painel de materiais"
          onMouseEnter={(e) => {
            if (!showMaterials)
              (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#1f2330";
          }}
          onMouseLeave={(e) => {
            if (!showMaterials)
              (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#1a1d25";
          }}
        >
          <FolderOpen size={13} />
          Materiais
          <span
            style={{
              fontSize: "9.5px",
              fontWeight: 700,
              color: showMaterials ? "#a5b4fc" : "#8b90a5",
              backgroundColor: showMaterials ? "rgba(99, 102, 241, 0.25)" : "#232733",
              borderRadius: "9999px",
              padding: "0px 5px",
              minWidth: "16px",
              textAlign: "center",
            }}
          >
            {materialsCount}
          </span>
        </button>
      </div>
    </header>
  );
}
