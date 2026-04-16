import React from "react";
import { Message } from "@/models/message";
import { MessageBubble } from "@/views/components/MessageBubble";
import { TypingIndicator } from "@/views/components/TypingIndicator";

interface ChatMessagesProps {
  messages: Message[];
  isTyping: boolean;
  messagesEndRef: React.RefObject<HTMLDivElement>;
}

export function ChatMessages({ messages, isTyping, messagesEndRef }: ChatMessagesProps) {
  return (
    <div
      className="flex-1 overflow-y-auto px-6 py-6"
      style={{ backgroundColor: "#f8f9fc" }}
    >
      <div className="flex items-center gap-3 mb-6">
        <div style={{ flex: 1, height: "0.5px", backgroundColor: "#e5e7ef" }} />
        <span style={{ fontSize: "10.5px", color: "#c0c4d8", padding: "0 4px" }}>
          Sessão iniciada hoje
        </span>
        <div style={{ flex: 1, height: "0.5px", backgroundColor: "#e5e7ef" }} />
      </div>

      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}

      {isTyping && <TypingIndicator />}

      <div ref={messagesEndRef} />
    </div>
  );
}
