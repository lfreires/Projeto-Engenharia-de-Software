import React from "react";
import { Server, Globe, Layers, Database, Zap } from "lucide-react";

const LAYERS = [
  {
    label: "Frontend",
    sublabel: "React · Next.js",
    icon: Globe,
    color: "#4338ca",
    bg: "#eef2ff",
    border: "#c7d2fe",
  },
  {
    label: "API Gateway",
    sublabel: "Kong · AWS",
    icon: Layers,
    color: "#5b21b6",
    bg: "#f5f3ff",
    border: "#ddd6fe",
  },
  {
    label: "Microserviços",
    sublabel: "Node.js · Python",
    icon: Server,
    color: "#6d28d9",
    bg: "#faf5ff",
    border: "#e9d5ff",
  },
  {
    label: "Banco de Dados",
    sublabel: "PostgreSQL · Redis",
    icon: Database,
    color: "#0369a1",
    bg: "#f0f9ff",
    border: "#bae6fd",
  },
];

export function AIImageResponse() {
  return (
    <div
      className="mt-3 rounded-xl overflow-hidden"
      style={{ border: "0.5px solid #dde2f0", backgroundColor: "#fafbff" }}
    >
      {/* Card header */}
      <div
        className="flex items-center gap-2 px-4 py-2.5"
        style={{ backgroundColor: "#f3f4f9", borderBottom: "0.5px solid #e5e8f0" }}
      >
        <div
          className="w-5 h-5 rounded flex items-center justify-center"
          style={{ backgroundColor: "#4f46e5" }}
        >
          <Zap size={11} fill="white" className="text-white" />
        </div>
        <span style={{ fontSize: "11px", fontWeight: 600, color: "#4338ca", letterSpacing: "0.04em" }}>
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
                    style={{ backgroundColor: layer.color }}
                  >
                    <Icon size={13} className="text-white" />
                  </div>
                  <div className="flex-1">
                    <div style={{ fontSize: "12px", fontWeight: 700, color: layer.color }}>
                      {layer.label}
                    </div>
                    <div style={{ fontSize: "10px", color: layer.color, opacity: 0.7 }}>
                      {layer.sublabel}
                    </div>
                  </div>
                  <div
                    className="text-right"
                    style={{ fontSize: "9.5px", color: layer.color, opacity: 0.6, fontWeight: 500 }}
                  >
                    {i === 0 ? "Interface" : i === 1 ? "Roteamento" : i === 2 ? "Domínio" : "Persistência"}
                  </div>
                </div>

                {i < LAYERS.length - 1 && (
                  <div className="flex justify-center">
                    <div style={{ width: "0.5px", height: "10px", backgroundColor: "#c7cad6" }} />
                  </div>
                )}
              </React.Fragment>
            );
          })}
        </div>

        <div
          className="flex items-center gap-1.5 mt-3 pt-2.5"
          style={{ borderTop: "0.5px solid #e8eaf4" }}
        >
          <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: "#818cf8" }} />
          <span style={{ fontSize: "9.5px", color: "#a0a4c0" }}>
            REST · gRPC · Kafka para eventos assíncronos
          </span>
        </div>
      </div>
    </div>
  );
}
