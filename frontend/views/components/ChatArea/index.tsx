import React from "react";
import { useChat } from "@/hooks/useChat";
import { getCurrentProject } from "@/services/projectService";
import { ConsultationHeader } from "@/views/components/ConsultationHeader";
import { ChatMessages } from "./ChatMessages";
import { ChatInput } from "./ChatInput";

interface ChatAreaProps {
  materialsCount: number;
  showMaterials: boolean;
  onToggleMaterials: () => void;
}

export function ChatArea({ materialsCount, showMaterials, onToggleMaterials }: ChatAreaProps) {
  const {
    messages,
    inputValue,
    isTyping,
    messagesEndRef,
    textareaRef,
    handleSend,
    handleSuggest,
    handleKeyDown,
    handleInput,
    clearChat,
  } = useChat();

  const project = getCurrentProject();

  return (
    <div className="flex flex-col flex-1 min-h-0 min-w-0 bg-white">
      <ConsultationHeader
        projectName={project.name}
        materialsCount={materialsCount}
        showMaterials={showMaterials}
        onToggleMaterials={onToggleMaterials}
        onNewChat={clearChat}
      />

      <ChatMessages
        messages={messages}
        isTyping={isTyping}
        messagesEndRef={messagesEndRef}
        onSuggestedQuestion={handleSuggest}
      />

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
