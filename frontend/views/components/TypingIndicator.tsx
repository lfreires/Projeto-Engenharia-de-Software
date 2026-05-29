import React from "react";
import { Sparkles } from "lucide-react";

export function TypingIndicator() {
  return (
    <div className="flex items-end gap-2.5 mb-5">
      <div
        className="shrink-0 w-6 h-6 rounded-md flex items-center justify-center"
        style={{ backgroundColor: "rgba(99, 102, 241, 0.18)", border: "0.5px solid rgba(99, 102, 241, 0.45)" }}
      >
        <Sparkles size={11} style={{ color: "#a5b4fc" }} />
      </div>

      <div
        className="flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl rounded-tl-sm"
        style={{ backgroundColor: "#14171f", border: "0.5px solid #232733" }}
      >
        <span
          className="w-1.5 h-1.5 rounded-full inline-block"
          style={{ backgroundColor: "#8b90a5", animation: "typing-bounce 1.2s ease-in-out infinite", animationDelay: "0ms" }}
        />
        <span
          className="w-1.5 h-1.5 rounded-full inline-block"
          style={{ backgroundColor: "#8b90a5", animation: "typing-bounce 1.2s ease-in-out infinite", animationDelay: "180ms" }}
        />
        <span
          className="w-1.5 h-1.5 rounded-full inline-block"
          style={{ backgroundColor: "#8b90a5", animation: "typing-bounce 1.2s ease-in-out infinite", animationDelay: "360ms" }}
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
