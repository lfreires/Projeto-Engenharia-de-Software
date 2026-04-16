import React from "react";
import { Sparkles } from "lucide-react";

export function TypingIndicator() {
  return (
    <div className="flex items-end gap-2.5 mb-5">
      <div
        className="shrink-0 w-6 h-6 rounded-md flex items-center justify-center"
        style={{ backgroundColor: "#eef2ff", border: "0.5px solid #c7d2fe" }}
      >
        <Sparkles size={11} style={{ color: "#4f46e5" }} />
      </div>

      <div
        className="flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl rounded-tl-sm"
        style={{ backgroundColor: "#f3f4f9", border: "0.5px solid #e5e7ef" }}
      >
        <span
          className="w-1.5 h-1.5 rounded-full inline-block"
          style={{ backgroundColor: "#a5a8c0", animation: "typing-bounce 1.2s ease-in-out infinite", animationDelay: "0ms" }}
        />
        <span
          className="w-1.5 h-1.5 rounded-full inline-block"
          style={{ backgroundColor: "#a5a8c0", animation: "typing-bounce 1.2s ease-in-out infinite", animationDelay: "180ms" }}
        />
        <span
          className="w-1.5 h-1.5 rounded-full inline-block"
          style={{ backgroundColor: "#a5a8c0", animation: "typing-bounce 1.2s ease-in-out infinite", animationDelay: "360ms" }}
        />
      </div>

      <style>{`
        @keyframes typing-bounce {
          0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
          30% { transform: translateY(-3px); opacity: 1; }
        }
      `}</style>
    </div>
  );
}
