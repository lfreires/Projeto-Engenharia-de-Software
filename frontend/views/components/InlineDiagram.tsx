import React from "react";

export function InlineDiagram() {
  return (
    <div
      className="mt-3 mb-1 rounded-lg p-4 inline-block w-full"
      style={{ border: "0.5px solid #232733", backgroundColor: "#14171f", maxWidth: "340px" }}
    >
      <p
        className="mb-3"
        style={{ fontSize: "9.5px", fontWeight: 600, color: "#6b7080", letterSpacing: "0.07em", textTransform: "uppercase" }}
      >
        Diagrama de Arquitetura
      </p>

      <div className="flex items-center gap-0">
        <div
          className="flex-1 text-center rounded-md py-2.5 px-2"
          style={{ border: "0.5px solid rgba(99, 102, 241, 0.4)", backgroundColor: "rgba(99, 102, 241, 0.15)" }}
        >
          <div style={{ fontSize: "10px", fontWeight: 700, color: "#a5b4fc" }}>Frontend</div>
          <div style={{ fontSize: "9px", color: "#818cf8", marginTop: "2px" }}>React / Next.js</div>
        </div>

        <div className="flex items-center shrink-0 px-1">
          <div style={{ width: "16px", height: "0.5px", backgroundColor: "#3a3f4d" }} />
          <svg width="5" height="8" viewBox="0 0 5 8" fill="none">
            <path d="M0 0L5 4L0 8" stroke="#3a3f4d" strokeWidth="0.5" fill="none" />
          </svg>
        </div>

        <div
          className="flex-1 text-center rounded-md py-2.5 px-2"
          style={{ border: "0.5px solid rgba(124, 58, 237, 0.4)", backgroundColor: "rgba(124, 58, 237, 0.18)" }}
        >
          <div style={{ fontSize: "10px", fontWeight: 700, color: "#c4b5fd" }}>API Gateway</div>
          <div style={{ fontSize: "9px", color: "#a78bfa", marginTop: "2px" }}>Kong / AWS</div>
        </div>

        <div className="flex items-center shrink-0 px-1">
          <div style={{ width: "16px", height: "0.5px", backgroundColor: "#3a3f4d" }} />
          <svg width="5" height="8" viewBox="0 0 5 8" fill="none">
            <path d="M0 0L5 4L0 8" stroke="#3a3f4d" strokeWidth="0.5" fill="none" />
          </svg>
        </div>

        <div
          className="flex-1 text-center rounded-md py-2.5 px-2"
          style={{ border: "0.5px solid rgba(168, 85, 247, 0.4)", backgroundColor: "rgba(168, 85, 247, 0.18)" }}
        >
          <div style={{ fontSize: "10px", fontWeight: 700, color: "#d8b4fe" }}>Microserviços</div>
          <div style={{ fontSize: "9px", color: "#c084fc", marginTop: "2px" }}>Node / Python</div>
        </div>
      </div>

      <div
        className="flex items-center gap-1.5 mt-3 pt-2.5"
        style={{ borderTop: "0.5px solid #232733" }}
      >
        <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: "#818cf8" }} />
        <span style={{ fontSize: "9px", color: "#8b90a5" }}>Comunicação via REST e gRPC</span>
      </div>
    </div>
  );
}
