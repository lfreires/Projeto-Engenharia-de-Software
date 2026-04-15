import React from "react";
import { Sparkles, FileText } from "lucide-react";
import { InlineDiagram } from "./InlineDiagram";

export type MessageRole = "ai" | "user";

export interface Message {
  id: string;
  role: MessageRole;
  content: string | React.ReactNode;
  citation?: string;
  hasDiagram?: boolean;
  timestamp: Date;
}

function CitationBadge({ source }: { source: string }) {
  return (
    <div className="mt-2 flex items-center gap-1.5">
      <span
        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full"
        style={{
          fontSize: "10.5px",
          fontWeight: 500,
          backgroundColor: "#f3f4f9",
          border: "0.5px solid #e0e3ef",
          color: "#7c80a0",
        }}
      >
        <FileText size={10} style={{ color: "#a0a4bc" }} />
        Fonte:{" "}
        <span style={{ color: "#4f46e5", fontWeight: 600 }}>{source}</span>
      </span>
    </div>
  );
}

function formatTime(date: Date) {
  return date.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
}

export function MessageBubble({ message }: { message: Message }) {
  const isAI = message.role === "ai";

  if (isAI) {
    return (
      <div className="flex items-start gap-2.5 mb-5" style={{ maxWidth: "80%" }}>
        {/* AI avatar */}
        <div
          className="shrink-0 w-6 h-6 rounded-md flex items-center justify-center mt-0.5"
          style={{
            backgroundColor: "#eef2ff",
            border: "0.5px solid #c7d2fe",
          }}
        >
          <Sparkles size={11} style={{ color: "#4f46e5" }} />
        </div>

        <div>
          <span
            className="block mb-1.5"
            style={{ fontSize: "10.5px", fontWeight: 500, color: "#b0b5c8" }}
          >
            DocAI · {formatTime(message.timestamp)}
          </span>

          <div
            className="rounded-xl rounded-tl-sm px-4 py-3"
            style={{
              backgroundColor: "#f3f4f9",
              border: "0.5px solid #e5e7ef",
            }}
          >
            <div style={{ fontSize: "13.5px", color: "#1e2035", lineHeight: "1.65" }}>
              {typeof message.content === "string" ? (
                <p style={{ margin: 0 }}>{message.content}</p>
              ) : (
                message.content
              )}
            </div>

            {message.hasDiagram && <InlineDiagram />}
          </div>

          {message.citation && <CitationBadge source={message.citation} />}
        </div>
      </div>
    );
  }

  // User bubble — right-aligned
  return (
    <div
      className="flex items-end justify-end gap-2.5 mb-5 ml-auto"
      style={{ maxWidth: "74%" }}
    >
      <div className="flex flex-col items-end">
        <span
          className="block mb-1.5"
          style={{ fontSize: "10.5px", fontWeight: 500, color: "#b0b5c8" }}
        >
          Você · {formatTime(message.timestamp)}
        </span>

        <div
          className="rounded-xl rounded-tr-sm px-4 py-3"
          style={{ backgroundColor: "#4f46e5" }}
        >
          <p
            className="text-white"
            style={{ fontSize: "13.5px", lineHeight: "1.65", margin: 0 }}
          >
            {message.content as string}
          </p>
        </div>
      </div>

      {/* User avatar */}
      <div
        className="shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-white"
        style={{
          background: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
          fontSize: "9px",
          fontWeight: 700,
        }}
      >
        JS
      </div>
    </div>
  );
}
