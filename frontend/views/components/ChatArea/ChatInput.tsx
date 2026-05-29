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
      style={{ borderTop: "0.5px solid #232733", backgroundColor: "#11141b" }}
    >
      <div className="px-5 pt-3 pb-3">
        <div
          className="flex items-center gap-2"
          style={{
            borderRadius: "10px",
            border: "0.5px solid #2a2f3d",
            backgroundColor: "#14171f",
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
            className="flex-1 resize-none bg-transparent outline-none placeholder:text-[#6b7080]"
            style={{
              fontSize: "13.5px",
              lineHeight: "1.5",
              color: "#e6e8ee",
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
              backgroundColor: canSend ? "#6366f1" : "#1f2330",
              cursor: canSend ? "pointer" : "default",
              marginBottom: "1px",
            }}
            title="Enviar"
          >
            <Send size={14} style={{ color: canSend ? "#ffffff" : "#5b6072" }} />
          </button>
        </div>

        <div className="flex items-center gap-1.5 mt-2 px-1">
          <Sparkles size={10} style={{ color: "#5b6072" }} />
          <p style={{ fontSize: "10.5px", color: "#6b7080", margin: 0 }}>
            A IA consulta apenas os documentos indexados do projeto
          </p>
        </div>
      </div>
    </div>
  );
}
