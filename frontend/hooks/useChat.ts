import React, { useState, useRef, useEffect, useCallback } from "react";
import { Message } from "@/models/message";
import { sendMessage } from "@/services/chatService";

function buildInitialMessages(): Message[] {
  return [
    {
      id: "ai-1",
      role: "ai",
      content: "Olá! Posso responder perguntas sobre os documentos deste projeto. Como posso ajudar?",
      timestamp: new Date(Date.now() - 5 * 60000),
    },
    {
      id: "user-1",
      role: "user",
      content: "Qual é a arquitetura do projeto?",
      timestamp: new Date(Date.now() - 4 * 60000),
    },
    {
      id: "ai-2",
      role: "ai",
      content: React.createElement(
        "div",
        { style: { fontSize: "13.5px", lineHeight: "1.65" } },
        React.createElement(
          "p",
          { style: { marginBottom: "10px" } },
          "O projeto adota uma arquitetura de ",
          React.createElement("strong", { style: { color: "#1e2035" } }, "microserviços"),
          ", projetada para alta escalabilidade e resiliência independente por domínio. Os três componentes principais são:"
        ),
        React.createElement(
          "div",
          { style: { display: "flex", flexDirection: "column", gap: "8px", marginBottom: "10px" } },
          ...[
            { dot: "#4f46e5", label: "Frontend", desc: "Aplicação React/Next.js — interface do cliente e painel administrativo" },
            { dot: "#7c3aed", label: "API Gateway", desc: "Ponto centralizado (Kong/AWS) — autenticação, rate limiting e roteamento" },
            { dot: "#9333ea", label: "Microserviços", desc: "Serviços independentes em Node.js e Python — pedidos, pagamentos, catálogo e usuários" },
          ].map((item) =>
            React.createElement(
              "div",
              { key: item.label, style: { display: "flex", gap: "8px", alignItems: "flex-start" } },
              React.createElement("div", {
                style: { width: "6px", height: "6px", borderRadius: "50%", backgroundColor: item.dot, marginTop: "7px", flexShrink: 0 },
              }),
              React.createElement(
                "span",
                null,
                React.createElement("strong", { style: { color: "#1e2035" } }, item.label),
                " — ",
                React.createElement("span", { style: { color: "#5a5f7a" } }, item.desc)
              )
            )
          )
        ),
        React.createElement(
          "p",
          { style: { fontSize: "12.5px", color: "#8b8fa8", margin: 0 } },
          "A comunicação entre serviços ocorre via REST e gRPC, com Kafka para eventos assíncronos entre domínios."
        )
      ),
      citation: "arquitetura.pdf",
      hasDiagram: true,
      timestamp: new Date(Date.now() - 3.5 * 60000),
    },
    {
      id: "user-2",
      role: "user",
      content: "Quais são as histórias de usuário do sprint atual?",
      timestamp: new Date(Date.now() - 2.5 * 60000),
    },
    {
      id: "ai-3",
      role: "ai",
      content: React.createElement(
        "div",
        { style: { fontSize: "13.5px", lineHeight: "1.65" } },
        React.createElement(
          "p",
          { style: { marginBottom: "12px" } },
          "As histórias de usuário do ",
          React.createElement("strong", { style: { color: "#1e2035" } }, "Sprint 7"),
          " (em andamento) são:"
        ),
        React.createElement(
          "div",
          { style: { display: "flex", flexDirection: "column", gap: "8px" } },
          ...[
            { id: "US-24", title: "Checkout com PIX", desc: "Como cliente, quero pagar com PIX para finalizar minha compra de forma rápida e sem taxas.", status: "Em andamento", statusBg: "#fefce8", statusColor: "#a16207", statusBorder: "#fde68a", pts: 8 },
            { id: "US-25", title: "Notificações de pedido", desc: "Como cliente, quero receber notificações por e-mail e push sobre o status do meu pedido.", status: "Concluída", statusBg: "#f0fdf4", statusColor: "#166534", statusBorder: "#bbf7d0", pts: 5 },
            { id: "US-26", title: "Filtros de catálogo avançados", desc: "Como usuário, quero filtrar produtos por preço, categoria e avaliação para encontrar o que procuro mais rápido.", status: "A fazer", statusBg: "#f8f9fc", statusColor: "#6b7280", statusBorder: "#e5e7eb", pts: 13 },
          ].map((story) =>
            React.createElement(
              "div",
              { key: story.id, style: { borderRadius: "8px", border: "0.5px solid #e5e8f0", backgroundColor: "#fafbff", padding: "10px 12px" } },
              React.createElement(
                "div",
                { style: { display: "flex", alignItems: "center", gap: "8px", marginBottom: "5px", flexWrap: "wrap" } },
                React.createElement("span", { style: { fontSize: "10px", fontWeight: 700, backgroundColor: "#eef2ff", color: "#4338ca", borderRadius: "4px", padding: "1px 6px" } }, story.id),
                React.createElement("span", { style: { fontSize: "13px", fontWeight: 600, color: "#1e2035", flex: 1 } }, story.title),
                React.createElement(
                  "div",
                  { style: { display: "flex", alignItems: "center", gap: "5px", marginLeft: "auto" } },
                  React.createElement("span", { style: { fontSize: "10px", fontWeight: 500, padding: "2px 8px", borderRadius: "9999px", backgroundColor: story.statusBg, color: story.statusColor, border: `0.5px solid ${story.statusBorder}` } }, story.status),
                  React.createElement("span", { style: { fontSize: "10px", color: "#a0a4b8", backgroundColor: "#f3f4f9", padding: "2px 6px", borderRadius: "4px" } }, `${story.pts} pts`)
                )
              ),
              React.createElement("p", { style: { fontSize: "12px", color: "#6b7080", lineHeight: "1.5", margin: 0 } }, story.desc)
            )
          )
        )
      ),
      citation: "sprints.xlsx",
      timestamp: new Date(Date.now() - 1.5 * 60000),
    },
  ];
}

export interface UseChatReturn {
  messages: Message[];
  inputValue: string;
  setInputValue: React.Dispatch<React.SetStateAction<string>>;
  isTyping: boolean;
  messagesEndRef: React.RefObject<HTMLDivElement>;
  textareaRef: React.RefObject<HTMLTextAreaElement>;
  handleSend: () => void;
  handleKeyDown: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void;
  handleInput: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>(() => buildInitialMessages());
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const handleSend = useCallback(() => {
    const trimmed = inputValue.trim();
    if (!trimmed || isTyping) return;

    const userMsg: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: trimmed,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputValue("");

    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }

    setIsTyping(true);

    sendMessage(trimmed).then((response) => {
      const aiMsg: Message = {
        id: `ai-${Date.now()}`,
        role: "ai",
        content: response,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMsg]);
      setIsTyping(false);
    });
  }, [inputValue, isTyping]);

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

  return { messages, inputValue, setInputValue, isTyping, messagesEndRef, textareaRef, handleSend, handleKeyDown, handleInput };
}
