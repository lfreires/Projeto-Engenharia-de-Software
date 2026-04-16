import React from "react";
import { Sparkles } from "lucide-react";

const SUGGESTIONS = [
  "Resuma o projeto",
  "Mostre a arquitetura da solução",
  "Quais são as histórias do sprint atual?",
  "Como funciona a autenticação?",
  "Quais são os módulos principais?",
  "Quais arquivos devo ler primeiro?",
  "Me mostre a documentação da API",
  "Como está o banco de dados?",
];

interface SuggestedQuestionsProps {
  onSelect: (question: string) => void;
}

export function SuggestedQuestions({ onSelect }: SuggestedQuestionsProps) {
  return (
    <div className="mt-2 mb-6">
      <div className="flex items-center gap-1.5 mb-3">
        <Sparkles size={11} style={{ color: "#a0a4c0" }} />
        <span style={{ fontSize: "11px", fontWeight: 500, color: "#a0a4c0", letterSpacing: "0.04em" }}>
          Sugestões de perguntas
        </span>
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
        {SUGGESTIONS.map((q) => (
          <button
            key={q}
            onClick={() => onSelect(q)}
            className="transition-all"
            style={{
              fontSize: "12px",
              fontWeight: 450,
              color: "#4f46e5",
              backgroundColor: "#f0f1ff",
              border: "0.5px solid #c7d2fe",
              borderRadius: "20px",
              padding: "5px 12px",
              cursor: "pointer",
              whiteSpace: "nowrap",
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#e0e7ff";
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#f0f1ff";
            }}
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
