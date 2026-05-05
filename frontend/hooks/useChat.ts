import React, { useState, useRef, useEffect, useCallback } from "react";
import { FeedbackRating, Message } from "@/models/message";
import { sendMessage, clearSession, sendFeedback } from "@/services/chatService";
import { PROJECT_ID } from "@/services/projectService";

// ─── Session management ───────────────────────────────────────────────────────

function getOrCreateSessionId(): string {
  const key = "docai_session_id";
  let id = sessionStorage.getItem(key);
  if (!id) {
    id = crypto.randomUUID();
    sessionStorage.setItem(key, id);
  }
  return id;
}

// ─── Welcome message ──────────────────────────────────────────────────────────

function buildWelcomeMessage(): Message {
  return {
    id: "ai-welcome",
    role: "ai",
    content:
      "Olá! Sou o **DocAI**, seu assistente de documentação para o projeto **E-commerce API**. Posso responder perguntas com base nos documentos indexados. O que você gostaria de saber?",
    timestamp: new Date(),
  };
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

export interface UseChatReturn {
  messages: Message[];
  inputValue: string;
  setInputValue: (v: string) => void;
  isTyping: boolean;
  messagesEndRef: React.RefObject<HTMLDivElement>;
  textareaRef: React.RefObject<HTMLTextAreaElement>;
  handleSend: () => void;
  handleSuggest: (question: string) => void;
  handleKeyDown: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void;
  handleInput: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  clearChat: () => void;
  submitFeedback: (messageId: string, rating: FeedbackRating) => void;
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([buildWelcomeMessage()]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const sessionIdRef = useRef<string>(getOrCreateSessionId());
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const submitQuestion = useCallback(
    (text: string) => {
      if (!text.trim() || isTyping) return;

      const userMsg: Message = {
        id: `user-${Date.now()}`,
        role: "user",
        content: text.trim(),
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMsg]);
      setIsTyping(true);

      sendMessage(text.trim(), PROJECT_ID, sessionIdRef.current)
        .then((payload) => {
          const aiMsg: Message = {
            id: `ai-${Date.now()}`,
            role: "ai",
            content: payload.content,
            citations: payload.citations,
            hasDiagram: payload.hasDiagram,
            hasImageCard: payload.hasImageCard,
            sprintStories: payload.sprintStories,
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, aiMsg]);
        })
        .catch((err: Error) => {
          const errMsg: Message = {
            id: `error-${Date.now()}`,
            role: "ai",
            content: err.message ?? "Não foi possível processar sua pergunta no momento. Por favor, tente novamente.",
            isError: true,
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, errMsg]);
        })
        .finally(() => {
          setIsTyping(false);
        });
    },
    [isTyping]
  );

  const handleSend = useCallback(() => {
    submitQuestion(inputValue);
    setInputValue("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  }, [inputValue, submitQuestion]);

  const handleSuggest = useCallback(
    (question: string) => {
      submitQuestion(question);
    },
    [submitQuestion]
  );

  const clearChat = useCallback(() => {
    clearSession(sessionIdRef.current).catch(() => {});
    // Generate a new session after clearing
    const newSessionId = crypto.randomUUID();
    sessionStorage.setItem("docai_session_id", newSessionId);
    sessionIdRef.current = newSessionId;

    setMessages([buildWelcomeMessage()]);
    setInputValue("");
    setIsTyping(false);
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  }, []);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend]
  );

  const handleInput = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
    const el = e.target;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 120) + "px";
  }, []);

  const submitFeedback = useCallback(
    (messageId: string, rating: FeedbackRating) => {
      // Optimistically update the local message state
      setMessages((prev) =>
        prev.map((m) => (m.id === messageId ? { ...m, feedback: rating } : m))
      );
      // Fire-and-forget — ignore errors silently (feedback is best-effort)
      sendFeedback(sessionIdRef.current, messageId, rating).catch(() => {});
    },
    []
  );

  return {
    messages,
    inputValue,
    setInputValue,
    isTyping,
    messagesEndRef,
    textareaRef,
    handleSend,
    handleSuggest,
    handleKeyDown,
    handleInput,
    clearChat,
    submitFeedback,
  };
}
