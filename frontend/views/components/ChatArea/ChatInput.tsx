import React from "react";
import { Send, Sparkles } from "lucide-react";

interface ChatInputProps {
  value: string;
  isTyping: boolean;
  textareaRef: React.RefObject<HTMLTextAreaElement>;
  onInput: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onKeyDown: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void;
  onSend: () => void;
}

export function ChatInput({ value, isTyping, textareaRef, onInput, onKeyDown, onSend }: ChatInputProps) {
  const canSend = !!value.trim() && !isTyping;

  return (
    <div
      className="shrink-0"
      style={{ borderTop: "0.5px solid #e2e5ee", backgroundColor: "#ffffff" }}
    >
      <div className="px-5 pt-3 pb-3">
        <div
          className="flex items-center gap-2"
          style={{
            borderRadius: "10px",
            border: "0.5px solid #dde0eb",
            backgroundColor: "#ffffff",
            padding: "10px 12px",
          }}
        >
          <textarea
            ref={textareaRef}
            rows={1}
            value={value}
            onChange={onInput}
            onKeyDown={onKeyDown}
            placeholder="Pergunte sobre o projeto..."
            className="flex-1 resize-none bg-transparent outline-none"
            style={{
              fontSize: "13.5px",
              lineHeight: "1.5",
              color: "#1e2035",
              maxHeight: "120px",
              minHeight: "22px",
              display: "block",
            }}
          />

          <button
            onClick={onSend}
            disabled={!canSend}
            className="shrink-0 w-8 h-8 rounded-lg flex items-center justify-center transition-colors"
            style={{
              backgroundColor: canSend ? "#4f46e5" : "#eef0f8",
              cursor: canSend ? "pointer" : "default",
              marginBottom: "1px",
            }}
            title="Enviar"
          >
            <Send size={14} style={{ color: canSend ? "#ffffff" : "#b0b5cc" }} />
          </button>
        </div>

        <div className="flex items-center gap-1.5 mt-2 px-1">
          <Sparkles size={10} style={{ color: "#d0d4e8" }} />
          <p style={{ fontSize: "10.5px", color: "#c0c4d8", margin: 0 }}>
            A IA consulta apenas os documentos indexados do projeto
          </p>
        </div>
      </div>
    </div>
  );
}
