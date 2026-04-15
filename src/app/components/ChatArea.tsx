import React, { useRef, useEffect, useState, KeyboardEvent } from "react";
import { Send, Sparkles } from "lucide-react";
import { MessageBubble, Message } from "./MessageBubble";
import { TypingIndicator } from "./TypingIndicator";

const PROJECT_NAME = "E-commerce API";

function buildInitialMessages(): Message[] {
  return [
    {
      id: "ai-1",
      role: "ai",
      content:
        "Olá! Posso responder perguntas sobre os documentos deste projeto. Como posso ajudar?",
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
      content: (
        <div style={{ fontSize: "13.5px", lineHeight: "1.65" }}>
          <p style={{ marginBottom: "10px" }}>
            O projeto adota uma arquitetura de{" "}
            <strong style={{ color: "#1e2035" }}>microserviços</strong>,
            projetada para alta escalabilidade e resiliência independente por domínio. Os três
            componentes principais são:
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginBottom: "10px" }}>
            {[
              {
                dot: "#4f46e5",
                label: "Frontend",
                desc: "Aplicação React/Next.js — interface do cliente e painel administrativo",
              },
              {
                dot: "#7c3aed",
                label: "API Gateway",
                desc: "Ponto centralizado (Kong/AWS) — autenticação, rate limiting e roteamento",
              },
              {
                dot: "#9333ea",
                label: "Microserviços",
                desc: "Serviços independentes em Node.js e Python — pedidos, pagamentos, catálogo e usuários",
              },
            ].map((item) => (
              <div key={item.label} style={{ display: "flex", gap: "8px", alignItems: "flex-start" }}>
                <div
                  style={{
                    width: "6px",
                    height: "6px",
                    borderRadius: "50%",
                    backgroundColor: item.dot,
                    marginTop: "7px",
                    flexShrink: 0,
                  }}
                />
                <span>
                  <strong style={{ color: "#1e2035" }}>{item.label}</strong>
                  {" — "}
                  <span style={{ color: "#5a5f7a" }}>{item.desc}</span>
                </span>
              </div>
            ))}
          </div>
          <p style={{ fontSize: "12.5px", color: "#8b8fa8", margin: 0 }}>
            A comunicação entre serviços ocorre via REST e gRPC, com Kafka para eventos
            assíncronos entre domínios.
          </p>
        </div>
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
      content: (
        <div style={{ fontSize: "13.5px", lineHeight: "1.65" }}>
          <p style={{ marginBottom: "12px" }}>
            As histórias de usuário do <strong style={{ color: "#1e2035" }}>Sprint 7</strong>{" "}
            (em andamento) são:
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {[
              {
                id: "US-24",
                title: "Checkout com PIX",
                desc: "Como cliente, quero pagar com PIX para finalizar minha compra de forma rápida e sem taxas.",
                status: "Em andamento",
                statusBg: "#fefce8",
                statusColor: "#a16207",
                statusBorder: "#fde68a",
                pts: 8,
              },
              {
                id: "US-25",
                title: "Notificações de pedido",
                desc: "Como cliente, quero receber notificações por e-mail e push sobre o status do meu pedido.",
                status: "Concluída",
                statusBg: "#f0fdf4",
                statusColor: "#166534",
                statusBorder: "#bbf7d0",
                pts: 5,
              },
              {
                id: "US-26",
                title: "Filtros de catálogo avançados",
                desc: "Como usuário, quero filtrar produtos por preço, categoria e avaliação para encontrar o que procuro mais rápido.",
                status: "A fazer",
                statusBg: "#f8f9fc",
                statusColor: "#6b7280",
                statusBorder: "#e5e7eb",
                pts: 13,
              },
            ].map((story) => (
              <div
                key={story.id}
                style={{
                  borderRadius: "8px",
                  border: "0.5px solid #e5e8f0",
                  backgroundColor: "#fafbff",
                  padding: "10px 12px",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    marginBottom: "5px",
                    flexWrap: "wrap",
                  }}
                >
                  <span
                    style={{
                      fontSize: "10px",
                      fontWeight: 700,
                      backgroundColor: "#eef2ff",
                      color: "#4338ca",
                      borderRadius: "4px",
                      padding: "1px 6px",
                    }}
                  >
                    {story.id}
                  </span>
                  <span style={{ fontSize: "13px", fontWeight: 600, color: "#1e2035", flex: 1 }}>
                    {story.title}
                  </span>
                  <div style={{ display: "flex", alignItems: "center", gap: "5px", marginLeft: "auto" }}>
                    <span
                      style={{
                        fontSize: "10px",
                        fontWeight: 500,
                        padding: "2px 8px",
                        borderRadius: "9999px",
                        backgroundColor: story.statusBg,
                        color: story.statusColor,
                        border: `0.5px solid ${story.statusBorder}`,
                      }}
                    >
                      {story.status}
                    </span>
                    <span
                      style={{
                        fontSize: "10px",
                        color: "#a0a4b8",
                        backgroundColor: "#f3f4f9",
                        padding: "2px 6px",
                        borderRadius: "4px",
                      }}
                    >
                      {story.pts} pts
                    </span>
                  </div>
                </div>
                <p style={{ fontSize: "12px", color: "#6b7080", lineHeight: "1.5", margin: 0 }}>
                  {story.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      ),
      citation: "sprints.xlsx",
      timestamp: new Date(Date.now() - 1.5 * 60000),
    },
  ];
}

export function ChatArea() {
  const [messages, setMessages] = useState<Message[]>(() => buildInitialMessages());
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(true); // starts with typing indicator visible
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const handleSend = () => {
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

    setTimeout(() => {
      const aiMsg: Message = {
        id: `ai-${Date.now()}`,
        role: "ai",
        content: `Com base nos documentos indexados do projeto ${PROJECT_NAME}, posso confirmar que "${trimmed}" é uma informação relevante. Para uma análise mais detalhada, recomendo consultar os arquivos da última ingestão ou refinar a pergunta com mais contexto.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMsg]);
      setIsTyping(false);
    }, 1800);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
    const el = e.target;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 120) + "px";
  };

  return (
    <div className="flex flex-col flex-1 min-h-0 bg-white">
      {/* Header */}
      <header
        className="shrink-0 flex items-center px-6"
        style={{
          height: "60px",
          borderBottom: "0.5px solid #e2e5ee",
          backgroundColor: "#ffffff",
        }}
      >
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1
              style={{
                fontSize: "15px",
                fontWeight: 600,
                color: "#111827",
                margin: 0,
              }}
            >
              Consulta ao Projeto
            </h1>

            {/* Status badge */}
            <span
              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full"
              style={{
                fontSize: "11px",
                fontWeight: 500,
                backgroundColor: "#f0fdf4",
                border: "0.5px solid #bbf7d0",
                color: "#166534",
              }}
            >
              <span
                className="w-1.5 h-1.5 rounded-full"
                style={{ backgroundColor: "#22c55e", display: "inline-block" }}
              />
              IA Conectada
            </span>
          </div>

          <p
            style={{
              fontSize: "11.5px",
              color: "#a0a4b8",
              margin: 0,
              marginTop: "1px",
            }}
          >
            Projeto:{" "}
            <span style={{ color: "#4f46e5", fontWeight: 500 }}>
              {PROJECT_NAME}
            </span>
          </p>
        </div>
      </header>

      {/* Message thread */}
      <div
        className="flex-1 overflow-y-auto px-6 py-6"
        style={{ backgroundColor: "#f8f9fc" }}
      >
        {/* Session label */}
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

      {/* Input bar */}
      <div
        className="shrink-0"
        style={{
          borderTop: "0.5px solid #e2e5ee",
          backgroundColor: "#ffffff",
        }}
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
              value={inputValue}
              onChange={handleInput}
              onKeyDown={handleKeyDown}
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
              onClick={handleSend}
              disabled={!inputValue.trim() || isTyping}
              className="shrink-0 w-8 h-8 rounded-lg flex items-center justify-center transition-colors"
              style={{
                backgroundColor:
                  inputValue.trim() && !isTyping ? "#4f46e5" : "#eef0f8",
                cursor:
                  inputValue.trim() && !isTyping ? "pointer" : "default",
                marginBottom: "1px",
              }}
              title="Enviar"
            >
              <Send
                size={14}
                style={{
                  color: inputValue.trim() && !isTyping ? "#ffffff" : "#b0b5cc",
                }}
              />
            </button>
          </div>

          {/* Hint */}
          <div className="flex items-center gap-1.5 mt-2 px-1">
            <Sparkles size={10} style={{ color: "#d0d4e8" }} />
            <p style={{ fontSize: "10.5px", color: "#c0c4d8", margin: 0 }}>
              A IA consulta apenas os documentos indexados do projeto
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}