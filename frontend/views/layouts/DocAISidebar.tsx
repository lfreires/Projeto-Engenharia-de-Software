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
  GitCommitHorizontal,
  ExternalLink,
} from "lucide-react";

type NavItem = {
  id: string;
  label: string;
  icon: React.ElementType;
  active: boolean;
  href?: string;
};

const NAV_ITEMS: readonly NavItem[] = [
  {
    id: "users",
    label: "Usuários e Projetos",
    icon: Users,
    active: false,
    href: "https://gerenciamento-projetos-users-e9fffgewdxe6gkfe.centralus-01.azurewebsites.net/#/login",
  },
  {
    id: "ingestion",
    label: "Ingestão de Dados",
    icon: Database,
    active: false,
    href: "https://mod2eng.azurewebsites.net/",
  },
  {
    id: "reports",
    label: "Relatórios",
    icon: FileBarChart2,
    active: false,
    href: "https://moduloderelatorios.azurewebsites.net/",
  },
  {
    id: "presentations",
    label: "Apresentações",
    icon: MonitorPlay,
    active: false,
    href: "https://modulo4-apresentacoes-v2.azurewebsites.net/docs",
  },
  {
    id: "diagrams",
    label: "Diagramas Técnicos",
    icon: GitBranch,
    active: false,
    href: "https://modulo5-interface-e-nuvem.azurewebsites.net/",
  },
  {
    id: "consultation",
    label: "Consulta",
    icon: MessageSquare,
    active: true,
  },
] as const;

export function DocAISidebar() {
  return (
    <aside
      className="flex flex-col h-full shrink-0"
      style={{
        width: "260px",
        minWidth: "260px",
        backgroundColor: "#11141b",
        borderRight: "0.5px solid #232733",
      }}
    >
      {/* Logo */}
      <div
        className="flex items-center gap-2.5 px-5"
        style={{ height: "60px", minHeight: "60px", borderBottom: "0.5px solid #232733" }}
      >
        <div
          className="w-7 h-7 rounded-md flex items-center justify-center shrink-0"
          style={{ backgroundColor: "#6366f1" }}
        >
          <Zap size={14} fill="white" className="text-white" />
        </div>
        <div>
          <span style={{ fontSize: "15px", fontWeight: 700, color: "#f3f4f9", letterSpacing: "-0.3px" }}>
            Doc<span style={{ color: "#a5b4fc" }}>AI</span>
          </span>
          <span
            className="block"
            style={{ fontSize: "9.5px", fontWeight: 500, color: "#6b7080", letterSpacing: "0.06em", marginTop: "-1px" }}
          >
            PLATAFORMA INTELIGENTE
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4 px-3">
        <p
          className="px-3 mb-2"
          style={{ fontSize: "9.5px", fontWeight: 600, color: "#6b7080", letterSpacing: "0.08em", textTransform: "uppercase" }}
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
                  style={{ backgroundColor: "rgba(99, 102, 241, 0.18)" }}
                >
                  <div
                    className="w-6 h-6 rounded-md flex items-center justify-center shrink-0"
                    style={{ backgroundColor: "#6366f1" }}
                  >
                    <Icon size={12} className="text-white" />
                  </div>
                  <span style={{ fontSize: "13px", fontWeight: 600, color: "#a5b4fc" }}>
                    {item.label}
                  </span>
                  <div className="ml-auto w-1.5 h-1.5 rounded-full shrink-0" style={{ backgroundColor: "#818cf8" }} />
                </div>
              );
            }
            return (
              <a
                key={item.id}
                href={item.href}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg group transition-colors"
                style={{
                  textDecoration: "none",
                  color: "inherit",
                  cursor: "pointer",
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLAnchorElement).style.backgroundColor = "#1a1d25";
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLAnchorElement).style.backgroundColor = "transparent";
                }}
                title={`Abrir ${item.label} em nova aba`}
              >
                <div
                  className="w-6 h-6 rounded-md flex items-center justify-center shrink-0"
                  style={{ backgroundColor: "#1a1d25", border: "0.5px solid #232733" }}
                >
                  <Icon size={12} style={{ color: "#8b90a5" }} />
                </div>
                <span style={{ fontSize: "13px", fontWeight: 500, color: "#c4c8d6", flex: 1 }}>
                  {item.label}
                </span>
                <ExternalLink size={11} style={{ color: "#5b6072", flexShrink: 0 }} />
              </a>
            );
          })}
        </div>

        {/* Divider */}
        <div className="my-4 mx-3" style={{ height: "0.5px", backgroundColor: "#232733" }} />

        {/* Module access note */}
        <div className="mx-3">
          <div
            className="px-3 py-2.5 rounded-lg"
            style={{ backgroundColor: "#14171f", border: "0.5px solid #232733" }}
          >
            <div className="flex items-start gap-2">
              <GitCommitHorizontal size={11} style={{ color: "#6b7080", marginTop: "2px", flexShrink: 0 }} />
              <p style={{ fontSize: "10.5px", color: "#8b90a5", lineHeight: 1.5, margin: 0 }}>
                Outros módulos disponíveis conforme permissão de acesso da equipe.
              </p>
            </div>
          </div>
        </div>
      </nav>

      {/* User footer */}
      <div
        className="px-4 py-3 flex items-center gap-2.5"
        style={{ borderTop: "0.5px solid #232733" }}
      >
        <div
          className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-white"
          style={{ background: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)", fontSize: "11px", fontWeight: 700 }}
        >
          JS
        </div>
        <div className="flex-1 min-w-0">
          <p style={{ fontSize: "13px", fontWeight: 600, color: "#f3f4f9", margin: 0 }}>João Silva</p>
          <p style={{ fontSize: "11px", color: "#8b90a5", margin: 0 }}>Tech Lead</p>
        </div>
        <button
          className="w-7 h-7 rounded-lg flex items-center justify-center"
          style={{ color: "#8b90a5", background: "none", border: "none", cursor: "pointer" }}
          title="Configurações"
        >
          <Settings size={14} />
        </button>
      </div>
    </aside>
  );
}
