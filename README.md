# Projeto - Engenharia de Software

> MVP do módulo de **Consulta ao Projeto**.

---

## Sobre o projeto

O **DocAI** é uma interface de chat com IA que permite aos membros de uma equipe consultar, de forma natural, os documentos técnicos de um projeto — arquitetura, backlog, API, banco de dados, onboarding e muito mais — sem precisar abrir arquivo por arquivo.

O sistema interpreta a pergunta do usuário, identifica a intenção e retorna uma resposta contextualizada com citação das fontes consultadas, diagramas visuais e cards estruturados quando apropriado.

---

## Funcionalidades

- **Chat com IA** — perguntas em linguagem natural sobre o projeto
- **Detecção de intenção** — respostas distintas para arquitetura, sprint, autenticação, API, banco de dados, onboarding e visão geral
- **Citações de fontes** — cada resposta indica quais documentos foram utilizados
- **Respostas ricas** — cards de sprint, diagramas de arquitetura e cards visuais por tipo de conteúdo
- **Painel de materiais** — lista dos documentos indexados do projeto com busca e filtragem
- **Perguntas sugeridas** — atalhos clicáveis para as consultas mais comuns
- **Nova consulta** — reset do histórico com um clique
- **Estado de erro** — tratamento visual de falhas na resposta da IA

---

## Stack

| Camada | Tecnologia |
|---|---|
| Framework | React 18 |
| Build | Vite 6 |
| Linguagem | TypeScript |
| Estilo | Tailwind CSS v4 |
| Componentes | shadcn/ui + Radix UI |
| Ícones | Lucide React |

---

## Estrutura do projeto

```
frontend/
├── main.tsx                          # Entry point
├── app/
│   ├── App.tsx                       # Composição raiz
│   └── styles/                       # CSS global, tema e fontes
├── views/
│   ├── layouts/
│   │   └── DocAISidebar.tsx          # Navegação lateral
│   └── components/
│       ├── ChatArea/
│       │   ├── index.tsx             # Orquestra o chat via useChat
│       │   ├── ChatMessages.tsx      # Lista de mensagens
│       │   └── ChatInput.tsx         # Input + botão enviar
│       ├── ConsultationHeader.tsx    # Header com status e ações
│       ├── MessageBubble.tsx         # Bolha de mensagem (AI / usuário)
│       ├── SuggestedQuestions.tsx    # Perguntas clicáveis
│       ├── CitationCard.tsx          # Card de fonte citada
│       ├── SprintStoriesCard.tsx     # Cards de histórias do sprint
│       ├── AIImageResponse.tsx       # Card visual de arquitetura
│       ├── ProjectMaterialsPanel.tsx # Painel lateral de materiais
│       ├── MaterialCard.tsx          # Card individual de material
│       ├── TypingIndicator.tsx       # Indicador de digitação da IA
│       └── InlineDiagram.tsx         # Diagrama de arquitetura inline
├── hooks/
│   ├── useChat.ts                    # Estado e lógica do chat
│   └── useMaterials.ts               # Estado do painel de materiais
├── services/
│   ├── chatService.ts                # Mock da IA com detecção de intenção
│   └── projectService.ts             # Dados mockados do projeto
├── models/
│   ├── message.ts                    # Message, MessageRole
│   ├── project.ts                    # Project, ProjectMaterial, SprintStory
│   ├── citation.ts                   # CitationSource
│   └── chat.ts                       # AIResponsePayload
├── utils/
│   ├── cn.ts                         # Utilitário de className
│   └── formatters.ts                 # Formatação de data/hora
└── types/
    └── index.ts                      # Re-exports centralizados
```

---

## Como rodar localmente

**Pré-requisito:** Node.js 18+

```bash
# Instalar dependências
npm install

# Rodar em modo desenvolvimento
npm run dev
```

Acesse `http://localhost:5173` no navegador.

```bash
# Gerar build de produção
npm run build
```

---

## Arquitetura do sistema (frontend + backend)

Diagrama considerando o frontend da branch `main` e o backend da branch `feat/productionize`.

```mermaid
graph TB
    subgraph Cliente
        U([Usuário])
        FE["Frontend React (Vite SPA)"]
    end

    subgraph Backend["query-service (FastAPI :8000)"]
        R[Router /api/v1/query]
        RAG[RAG Pipeline]
        EMB[Embedder local (all-MiniLM-L6-v2)]
        RET[Retriever]
        LLM[LLM Client (Groq)]
        R --> RAG
        RAG --> EMB
        RAG --> RET
        RAG --> LLM
    end

    subgraph Azure
        SEARCH[(Azure AI Search)]
        KV[Key Vault]
    end

    subgraph Groq
        G70["llama-3.3-70b-versatile"]
        G8["llama-3.1-8b-instant (fallback)"]
    end

    U -->|pergunta| FE
    FE -->|"POST /api/v1/query/chat"| R
    RET -->|"vector search"| SEARCH
    LLM -->|"chat completion"| G70
    G70 -.->|"429"| G8
    KV -->|secret| LLM
    R -->|"resposta + citações"| FE
    FE -->|resposta| U
```

## Arquitetura de frontend

O projeto segue uma abordagem inspirada em **MVC adaptado para frontend moderno**:

| Camada | Responsabilidade |
|---|---|
| `views/` | Interface — páginas, layouts e componentes visuais |
| `hooks/` | Orquestração de lógica e estado (equivalente ao controller) |
| `models/` | Contratos de domínio e tipos centrais |
| `services/` | Comunicação com APIs externas e acesso a dados |
| `utils/` | Funções puras e helpers reutilizáveis |

Toda a lógica do chat vive em `useChat.ts`. Os componentes são puramente apresentacionais e recebem dados via props. A comunicação com a IA é abstraída em `chatService.ts`, com uma interface que não muda ao integrar o backend real.

---

## Perguntas suportadas pelo mock

As seguintes perguntas ativam respostas:

| Pergunta | Tipo de resposta |
|---|---|
| Resuma o projeto | Visão geral + card visual |
| Mostre a arquitetura da solução | Diagrama de camadas + card de arquitetura |
| Quais são as histórias do sprint atual? | Cards do Sprint 7 com status e pontuação |
| Como funciona a autenticação? | Explicação JWT + citações de auth-flow.md e swagger.yaml |
| Quais são os módulos principais? | Lista dos 4 microserviços + diagrama |
| Quais arquivos devo ler primeiro? | Guia de onboarding com ordem recomendada |
| Me mostre a documentação da API | Resumo OpenAPI + citação do swagger.yaml |
| Como está o banco de dados? | Resumo do schema PostgreSQL + citação do db-schema.sql |

Qualquer outra pergunta retorna uma resposta de fallback coerente.

---

## O que está mockado

| O quê | Onde |
|---|---|
| Resposta da IA | `services/chatService.ts` |
| Dados do projeto (nome, sprint, equipe) | `services/projectService.ts` |
| Lista de materiais (8 documentos) | `services/projectService.ts` |
| Citações e trechos de evidência | `services/chatService.ts` |
| Usuário logado | `views/layouts/DocAISidebar.tsx` |

---

## Integrando o backend

A arquitetura foi desenhada para que a substituição dos mocks seja cirúrgica — nenhum componente precisa mudar:

```ts
// services/chatService.ts

// Hoje (mock):
export async function sendMessage(query: string): Promise<AIResponsePayload> {
  await delay(1600);
  return RESPONSES[detectIntent(query)]();
}

// Com backend real, basta trocar o corpo da função:
export async function sendMessage(query: string): Promise<AIResponsePayload> {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  return res.json(); // mesmo formato AIResponsePayload
}
```

---

## Disciplina

Projeto desenvolvido para a disciplina de **Engenharia de Software**.
