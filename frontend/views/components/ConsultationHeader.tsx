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
      style={{ height: "60px", borderBottom: "0.5px solid #e2e5ee", backgroundColor: "#ffffff" }}
    >
      {/* Left — title + project */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2.5">
          <h1 style={{ fontSize: "15px", fontWeight: 600, color: "#111827", margin: 0 }}>
            Consulta ao Projeto
          </h1>

          <span
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full"
            style={{
              fontSize: "10.5px",
              fontWeight: 500,
              backgroundColor: "#f0fdf4",
              border: "0.5px solid #bbf7d0",
              color: "#166534",
            }}
          >
            <span
              className="w-1.5 h-1.5 rounded-full"
              style={{ backgroundColor: "#22c55e", display: "inline-block" }}
            />
            IA Ativa
          </span>
        </div>

        <p style={{ fontSize: "11.5px", color: "#a0a4b8", margin: 0, marginTop: "1px" }}>
          Projeto:{" "}
          <span style={{ color: "#4f46e5", fontWeight: 500 }}>{projectName}</span>
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
            color: "#7c80a0",
            backgroundColor: "#f3f4f9",
            border: "0.5px solid #e0e3ef",
            cursor: "pointer",
          }}
          title="Nova consulta"
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#e8eaf2";
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#f3f4f9";
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
            color: showMaterials ? "#4f46e5" : "#7c80a0",
            backgroundColor: showMaterials ? "#eef2ff" : "#f3f4f9",
            border: showMaterials ? "0.5px solid #c7d2fe" : "0.5px solid #e0e3ef",
            cursor: "pointer",
          }}
          title="Painel de materiais"
          onMouseEnter={(e) => {
            if (!showMaterials)
              (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#e8eaf2";
          }}
          onMouseLeave={(e) => {
            if (!showMaterials)
              (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#f3f4f9";
          }}
        >
          <FolderOpen size={13} />
          Materiais
          <span
            style={{
              fontSize: "9.5px",
              fontWeight: 700,
              color: showMaterials ? "#4f46e5" : "#a0a4b8",
              backgroundColor: showMaterials ? "#dde5ff" : "#e8eaf0",
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
