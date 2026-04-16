import React from "react";
import { useChat } from "@/hooks/useChat";
import { ChatMessages } from "./ChatMessages";
import { ChatInput } from "./ChatInput";

const PROJECT_NAME = "E-commerce API";

export function ChatArea() {
  const { messages, inputValue, isTyping, messagesEndRef, textareaRef, handleSend, handleKeyDown, handleInput } =
    useChat();

  return (
    <div className="flex flex-col flex-1 min-h-0 bg-white">
      <header
        className="shrink-0 flex items-center px-6"
        style={{ height: "60px", borderBottom: "0.5px solid #e2e5ee", backgroundColor: "#ffffff" }}
      >
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 style={{ fontSize: "15px", fontWeight: 600, color: "#111827", margin: 0 }}>
              Consulta ao Projeto
            </h1>

            <span
              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full"
              style={{ fontSize: "11px", fontWeight: 500, backgroundColor: "#f0fdf4", border: "0.5px solid #bbf7d0", color: "#166534" }}
            >
              <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: "#22c55e", display: "inline-block" }} />
              IA Conectada
            </span>
          </div>

          <p style={{ fontSize: "11.5px", color: "#a0a4b8", margin: 0, marginTop: "1px" }}>
            Projeto:{" "}
            <span style={{ color: "#4f46e5", fontWeight: 500 }}>{PROJECT_NAME}</span>
          </p>
        </div>
      </header>

      <ChatMessages messages={messages} isTyping={isTyping} messagesEndRef={messagesEndRef} />

      <ChatInput
        value={inputValue}
        isTyping={isTyping}
        textareaRef={textareaRef}
        onInput={handleInput}
        onKeyDown={handleKeyDown}
        onSend={handleSend}
      />
    </div>
  );
}
