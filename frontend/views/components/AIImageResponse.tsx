import React from "react";
import { Server, Globe, Layers, Database, Zap } from "lucide-react";

const LAYERS = [
  {
    label: "Frontend",
    sublabel: "React · Next.js",
    icon: Globe,
    color: "#a5b4fc",
    bg: "rgba(99, 102, 241, 0.15)",
    border: "rgba(99, 102, 241, 0.4)",
  },
  {
    label: "API Gateway",
    sublabel: "Kong · AWS",
    icon: Layers,
    color: "#c4b5fd",
    bg: "rgba(124, 58, 237, 0.18)",
    border: "rgba(124, 58, 237, 0.4)",
  },
  {
    label: "Microserviços",
    sublabel: "Node.js · Python",
    icon: Server,
    color: "#d8b4fe",
    bg: "rgba(168, 85, 247, 0.18)",
    border: "rgba(168, 85, 247, 0.4)",
  },
  {
    label: "Banco de Dados",
    sublabel: "PostgreSQL · Redis",
    icon: Database,
    color: "#7dd3fc",
    bg: "rgba(14, 165, 233, 0.18)",
    border: "rgba(14, 165, 233, 0.4)",
  },
];

export function AIImageResponse() {
  return (
    <div
      className="mt-3 rounded-xl overflow-hidden"
      style={{ border: "0.5px solid #232733", backgroundColor: "#14171f" }}
    >
      {/* Card header */}
      <div
        className="flex items-center gap-2 px-4 py-2.5"
        style={{ backgroundColor: "#1a1d25", borderBottom: "0.5px solid #232733" }}
      >
        <div
          className="w-5 h-5 rounded flex items-center justify-center"
          style={{ backgroundColor: "#6366f1" }}
        >
          <Zap size={11} fill="white" className="text-white" />
        </div>
        <span style={{ fontSize: "11px", fontWeight: 600, color: "#a5b4fc", letterSpacing: "0.04em" }}>
          VISÃO GERAL DO SISTEMA
        </span>
      </div>

      {/* Architecture layers */}
      <div className="p-4">
        <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
          {LAYERS.map((layer, i) => {
            const Icon = layer.icon;
            return (
              <React.Fragment key={layer.label}>
                <div
                  className="flex items-center gap-3 rounded-lg px-3 py-2.5"
                  style={{ backgroundColor: layer.bg, border: `0.5px solid ${layer.border}` }}
                >
                  <div
                    className="w-7 h-7 rounded-md flex items-center justify-center shrink-0"
                    style={{ backgroundColor: "rgba(0, 0, 0, 0.25)", border: `0.5px solid ${layer.border}` }}
                  >
                    <Icon size={13} style={{ color: layer.color }} />
                  </div>
                  <div className="flex-1">
                    <div style={{ fontSize: "12px", fontWeight: 700, color: layer.color }}>
                      {layer.label}
                    </div>
                    <div style={{ fontSize: "10px", color: layer.color, opacity: 0.75 }}>
                      {layer.sublabel}
                    </div>
                  </div>
                  <div
                    className="text-right"
                    style={{ fontSize: "9.5px", color: layer.color, opacity: 0.7, fontWeight: 500 }}
                  >
                    {i === 0 ? "Interface" : i === 1 ? "Roteamento" : i === 2 ? "Domínio" : "Persistência"}
                  </div>
                </div>

                {i < LAYERS.length - 1 && (
                  <div className="flex justify-center">
                    <div style={{ width: "0.5px", height: "10px", backgroundColor: "#2a2f3d" }} />
                  </div>
                )}
              </React.Fragment>
            );
          })}
        </div>

        <div
          className="flex items-center gap-1.5 mt-3 pt-2.5"
          style={{ borderTop: "0.5px solid #232733" }}
        >
          <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: "#818cf8" }} />
          <span style={{ fontSize: "9.5px", color: "#8b90a5" }}>
            REST · gRPC · Kafka para eventos assíncronos
          </span>
        </div>
      </div>
    </div>
  );
}
