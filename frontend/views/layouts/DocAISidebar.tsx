import React from "react";
import {
  Zap,
  Users,
  Database,
  FileBarChart2,
  MonitorPlay,
  GitBranch,
  MessageSquare,
  Settings,
} from "lucide-react";

const NAV_ITEMS = [
  { id: "users", label: "Usuários e Projetos", icon: Users, active: false },
  { id: "ingestion", label: "Ingestão de Dados", icon: Database, active: false },
  { id: "reports", label: "Relatórios", icon: FileBarChart2, active: false },
  { id: "presentations", label: "Apresentações", icon: MonitorPlay, active: false },
  { id: "diagrams", label: "Diagramas Técnicos", icon: GitBranch, active: false },
  { id: "consultation", label: "Consulta", icon: MessageSquare, active: true },
] as const;

export function DocAISidebar() {
  return (
    <aside
      className="flex flex-col h-full bg-white shrink-0"
      style={{ width: "260px", minWidth: "260px", borderRight: "0.5px solid #e2e5ee" }}
    >
      {/* Logo */}
      <div
        className="flex items-center gap-2.5 px-5"
        style={{ height: "60px", minHeight: "60px", borderBottom: "0.5px solid #e2e5ee" }}
      >
        <div
          className="w-7 h-7 rounded-md flex items-center justify-center shrink-0"
          style={{ backgroundColor: "#4f46e5" }}
        >
          <Zap size={14} fill="white" className="text-white" />
        </div>
        <div>
          <span style={{ fontSize: "15px", fontWeight: 700, color: "#111827", letterSpacing: "-0.3px" }}>
            Doc<span style={{ color: "#4f46e5" }}>AI</span>
          </span>
          <span
            className="block"
            style={{ fontSize: "9.5px", fontWeight: 500, color: "#b0b5c8", letterSpacing: "0.06em", marginTop: "-1px" }}
          >
            PLATAFORMA INTELIGENTE
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4 px-3">
        <p
          className="px-3 mb-2"
          style={{ fontSize: "9.5px", fontWeight: 600, color: "#c0c4d6", letterSpacing: "0.08em", textTransform: "uppercase" }}
        >
          Módulos
        </p>

        <div className="space-y-0.5">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            if (item.active) {
              return (
                <div
                  key={item.id}
                  className="flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer"
                  style={{ backgroundColor: "#eef2ff" }}
                >
                  <div
                    className="w-6 h-6 rounded-md flex items-center justify-center shrink-0"
                    style={{ backgroundColor: "#4f46e5" }}
                  >
                    <Icon size={12} className="text-white" />
                  </div>
                  <span style={{ fontSize: "13px", fontWeight: 600, color: "#4f46e5" }}>
                    {item.label}
                  </span>
                  <div className="ml-auto w-1.5 h-1.5 rounded-full shrink-0" style={{ backgroundColor: "#4f46e5" }} />
                </div>
              );
            }

            return (
              <div
                key={item.id}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg"
                style={{ cursor: "default", opacity: 0.45 }}
              >
                <div
                  className="w-6 h-6 rounded-md flex items-center justify-center shrink-0"
                  style={{ backgroundColor: "#f0f1f7" }}
                >
                  <Icon size={12} style={{ color: "#9095b0" }} />
                </div>
                <span style={{ fontSize: "13px", fontWeight: 400, color: "#6b7080" }}>
                  {item.label}
                </span>
              </div>
            );
          })}
        </div>

        <div className="my-4 mx-3" style={{ height: "0.5px", backgroundColor: "#e8eaf0" }} />

        <div
          className="mx-3 px-3 py-2.5 rounded-lg"
          style={{ backgroundColor: "#f7f8fc", border: "0.5px solid #e8eaf0" }}
        >
          <p style={{ fontSize: "11px", color: "#9095b0", lineHeight: 1.5 }}>
            Outros módulos estão disponíveis conforme permissão de acesso da sua equipe.
          </p>
        </div>
      </nav>

      {/* User footer */}
      <div
        className="px-4 py-3 flex items-center gap-2.5"
        style={{ borderTop: "0.5px solid #e2e5ee" }}
      >
        <div
          className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-white"
          style={{ background: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)", fontSize: "11px", fontWeight: 700 }}
        >
          JS
        </div>
        <div className="flex-1 min-w-0">
          <p style={{ fontSize: "13px", fontWeight: 600, color: "#111827" }}>João Silva</p>
          <p style={{ fontSize: "11px", color: "#a0a4b8" }}>Tech Lead</p>
        </div>
        <button
          className="w-7 h-7 rounded-lg flex items-center justify-center"
          style={{ color: "#c0c4d6" }}
          title="Configurações"
        >
          <Settings size={14} />
        </button>
      </div>
    </aside>
  );
}
