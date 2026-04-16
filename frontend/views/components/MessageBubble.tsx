import React from "react";
import { Sparkles, AlertCircle } from "lucide-react";
import { Message } from "@/models/message";
import { formatTime } from "@/utils/formatters";
import { InlineDiagram } from "./InlineDiagram";
import { AIImageResponse } from "./AIImageResponse";
import { CitationCard } from "./CitationCard";
import { SprintStoriesCard } from "./SprintStoriesCard";

function renderContent(content: string) {
  // Simple bold rendering: **text** → <strong>text</strong>
  const parts = content.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i} style={{ color: "#1e2035" }}>{part.slice(2, -2)}</strong>;
    }
    // Handle line breaks
    return part.split("\n").map((line, j, arr) => (
      <React.Fragment key={`${i}-${j}`}>
        {line}
        {j < arr.length - 1 && <br />}
      </React.Fragment>
    ));
  });
}

export function MessageBubble({ message }: { message: Message }) {
  const isAI = message.role === "ai";

  if (!isAI) {
    return (
      <div
        className="flex items-end justify-end gap-2.5 mb-5 ml-auto"
        style={{ maxWidth: "72%" }}
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
            <p className="text-white" style={{ fontSize: "13.5px", lineHeight: "1.65", margin: 0 }}>
              {message.content}
            </p>
          </div>
        </div>

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

  // AI message
  return (
    <div className="flex items-start gap-2.5 mb-5" style={{ maxWidth: "84%" }}>
      {/* Avatar */}
      <div
        className="shrink-0 w-6 h-6 rounded-md flex items-center justify-center mt-0.5"
        style={{
          backgroundColor: message.isError ? "#fef2f2" : "#eef2ff",
          border: `0.5px solid ${message.isError ? "#fecaca" : "#c7d2fe"}`,
        }}
      >
        {message.isError ? (
          <AlertCircle size={11} style={{ color: "#dc2626" }} />
        ) : (
          <Sparkles size={11} style={{ color: "#4f46e5" }} />
        )}
      </div>

      <div style={{ flex: 1, minWidth: 0 }}>
        <span
          className="block mb-1.5"
          style={{ fontSize: "10.5px", fontWeight: 500, color: "#b0b5c8" }}
        >
          DocAI · {formatTime(message.timestamp)}
        </span>

        {/* Bubble */}
        <div
          className="rounded-xl rounded-tl-sm px-4 py-3"
          style={{
            backgroundColor: message.isError ? "#fff5f5" : "#f3f4f9",
            border: `0.5px solid ${message.isError ? "#fecaca" : "#e5e7ef"}`,
          }}
        >
          <div style={{ fontSize: "13.5px", color: "#1e2035", lineHeight: "1.7" }}>
            {renderContent(message.content)}
          </div>

          {message.hasDiagram && <InlineDiagram />}
          {message.hasImageCard && <AIImageResponse />}
          {message.sprintStories && message.sprintStories.length > 0 && (
            <SprintStoriesCard stories={message.sprintStories} />
          )}
        </div>

        {/* Citations */}
        {message.citations && message.citations.length > 0 && (
          <div className="mt-2">
            <p style={{ fontSize: "10.5px", fontWeight: 500, color: "#b0b5c8", marginBottom: "4px" }}>
              Fontes consultadas
            </p>
            {message.citations.map((cit) => (
              <CitationCard key={cit.id} citation={cit} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
