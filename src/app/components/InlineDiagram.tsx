import React from "react";

export function InlineDiagram() {
  return (
    <div
      className="mt-3 mb-1 rounded-lg p-4 inline-block w-full"
      style={{
        border: "0.5px solid #dde2f0",
        backgroundColor: "#fafbff",
        maxWidth: "340px",
      }}
    >
      <p
        className="mb-3"
        style={{
          fontSize: "9.5px",
          fontWeight: 600,
          color: "#a0a4b8",
          letterSpacing: "0.07em",
          textTransform: "uppercase",
        }}
      >
        Diagrama de Arquitetura
      </p>

      <div className="flex items-center gap-0">
        {/* Frontend */}
        <div
          className="flex-1 text-center rounded-md py-2.5 px-2"
          style={{
            border: "0.5px solid #c7d2fe",
            backgroundColor: "#eef2ff",
          }}
        >
          <div style={{ fontSize: "10px", fontWeight: 700, color: "#4338ca" }}>
            Frontend
          </div>
          <div style={{ fontSize: "9px", color: "#818cf8", marginTop: "2px" }}>
            React / Next.js
          </div>
        </div>

        {/* Arrow */}
        <div className="flex items-center shrink-0 px-1">
          <div style={{ width: "16px", height: "0.5px", backgroundColor: "#c7cad6" }} />
          <svg width="5" height="8" viewBox="0 0 5 8" fill="none">
            <path d="M0 0L5 4L0 8" stroke="#c7cad6" strokeWidth="0.5" fill="none" />
          </svg>
        </div>

        {/* API Gateway */}
        <div
          className="flex-1 text-center rounded-md py-2.5 px-2"
          style={{
            border: "0.5px solid #ddd6fe",
            backgroundColor: "#f5f3ff",
          }}
        >
          <div style={{ fontSize: "10px", fontWeight: 700, color: "#5b21b6" }}>
            API Gateway
          </div>
          <div style={{ fontSize: "9px", color: "#a78bfa", marginTop: "2px" }}>
            Kong / AWS
          </div>
        </div>

        {/* Arrow */}
        <div className="flex items-center shrink-0 px-1">
          <div style={{ width: "16px", height: "0.5px", backgroundColor: "#c7cad6" }} />
          <svg width="5" height="8" viewBox="0 0 5 8" fill="none">
            <path d="M0 0L5 4L0 8" stroke="#c7cad6" strokeWidth="0.5" fill="none" />
          </svg>
        </div>

        {/* Microservices */}
        <div
          className="flex-1 text-center rounded-md py-2.5 px-2"
          style={{
            border: "0.5px solid #e9d5ff",
            backgroundColor: "#faf5ff",
          }}
        >
          <div style={{ fontSize: "10px", fontWeight: 700, color: "#7e22ce" }}>
            Microserviços
          </div>
          <div style={{ fontSize: "9px", color: "#c084fc", marginTop: "2px" }}>
            Node / Python
          </div>
        </div>
      </div>

      <div
        className="flex items-center gap-1.5 mt-3 pt-2.5"
        style={{ borderTop: "0.5px solid #e8eaf4" }}
      >
        <div
          className="w-1.5 h-1.5 rounded-full"
          style={{ backgroundColor: "#818cf8" }}
        />
        <span style={{ fontSize: "9px", color: "#b0b5cc" }}>
          Comunicação via REST e gRPC
        </span>
      </div>
    </div>
  );
}
