import React from "react";
import { useChat } from "@/hooks/useChat";
import { ConsultationHeader } from "@/views/components/ConsultationHeader";
import { ChatInput } from "./ChatInput";
import { ChatMessages } from "./ChatMessages";

interface ChatAreaProps {
  materialsCount: number;
  projectName: string;
  showMaterials: boolean;
  onToggleMaterials: () => void;
  onConnectionError: (message: string | null) => void;
}

export function ChatArea({
  materialsCount,
  projectName,
  showMaterials,
  onToggleMaterials,
  onConnectionError,
}: ChatAreaProps) {
  const {
    messages,
    inputValue,
    isTyping,
    connectionError,
    messagesEndRef,
    textareaRef,
    handleSend,
    handleSuggest,
    handleKeyDown,
    handleInput,
    clearChat,
    submitFeedback,
  } = useChat();

  React.useEffect(() => {
    onConnectionError(connectionError);
  }, [connectionError, onConnectionError]);

  return (
    <div className="flex flex-col flex-1 min-h-0 min-w-0 bg-white">
      <ConsultationHeader
        projectName={projectName}
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
        onFeedback={submitFeedback}
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
