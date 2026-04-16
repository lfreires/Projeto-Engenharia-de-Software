import { AIResponsePayload } from "@/models/chat";
import { CitationSource } from "@/models/citation";
import { SprintStory } from "@/models/project";

// ─── Helpers ──────────────────────────────────────────────────────────────────

type Intent =
  | "overview"
  | "architecture"
  | "sprint"
  | "auth"
  | "api"
  | "modules"
  | "onboarding"
  | "database"
  | "default";

function containsAny(text: string, keywords: string[]): boolean {
  return keywords.some((kw) => text.includes(kw));
}

function detectIntent(query: string): Intent {
  const q = query.toLowerCase();
  if (containsAny(q, ["resumo", "resumir", "resuma", "sobre o projeto", "visão geral", "overview", "apresentar", "me fale sobre"])) return "overview";
  if (containsAny(q, ["arquitetura", "diagrama", "estrutura", "como funciona", "componentes", "fluxo de dados", "infraestrutura", "sistema"])) return "architecture";
  if (containsAny(q, ["sprint", "história", "us-", "backlog", "iteração", "kanban", "scrum", "andamento", "atual"])) return "sprint";
  if (containsAny(q, ["autenticação", "auth", "login", "jwt", "segurança", "permissão", "acesso", "token", "refresh"])) return "auth";
  if (containsAny(q, ["api", "endpoint", "swagger", "openapi", "documentação", "rota", "método", "rest", "http"])) return "api";
  if (containsAny(q, ["módulo", "funcionalidade", "feature", "principal", "serviço", "microserviço"])) return "modules";
  if (containsAny(q, ["arquivo", "ler primeiro", "começar", "onboarding", "orientação", "novo membro", "setup"])) return "onboarding";
  if (containsAny(q, ["banco", "database", "schema", "tabela", "sql", "dado", "postgresql", "relacion"])) return "database";
  return "default";
}

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ─── Mock citations ────────────────────────────────────────────────────────────

const CITATIONS: Record<string, CitationSource> = {
  arquitetura: {
    id: "cit-arq",
    filename: "arquitetura.pdf",
    type: "pdf",
    excerpt:
      "O projeto adota arquitetura de microserviços com Frontend, API Gateway (Kong/AWS) e serviços independentes em Node.js e Python.",
    materialId: "mat-01",
  },
  swagger: {
    id: "cit-swagger",
    filename: "swagger.yaml",
    type: "yaml",
    excerpt:
      "Especificação OpenAPI 3.0. Base path: /api/v1. Autenticação: Bearer JWT. 47 endpoints documentados em 8 recursos.",
    materialId: "mat-02",
  },
  sprint: {
    id: "cit-sprint",
    filename: "sprint7-ata.xlsx",
    type: "spreadsheet",
    excerpt:
      "Sprint 7 — 26 pontos no total. 3 histórias ativas. Velocidade média da equipe: 24 pontos por sprint.",
    materialId: "mat-03",
  },
  readme: {
    id: "cit-readme",
    filename: "README.md",
    type: "markdown",
    excerpt:
      "Stack principal: Node.js 20, React 18, PostgreSQL 15, Kafka 3.6, Kong Gateway. Ambiente local via Docker Compose.",
    materialId: "mat-04",
  },
  auth: {
    id: "cit-auth",
    filename: "auth-flow.md",
    type: "markdown",
    excerpt:
      "Autenticação via JWT com access token (15min) e refresh token (7 dias). Escopos: read, write, admin. PKCE para clientes públicos.",
    materialId: "mat-05",
  },
  backlog: {
    id: "cit-backlog",
    filename: "backlog.xlsx",
    type: "spreadsheet",
    excerpt:
      "42 itens no backlog do produto. Prioridade alta: Checkout PIX, Notificações push, Catálogo v2. Estimativa total: 187 pontos.",
    materialId: "mat-06",
  },
  dbSchema: {
    id: "cit-db",
    filename: "db-schema.sql",
    type: "sql",
    excerpt:
      "PostgreSQL 15. Tabelas principais: users, products, orders, order_items, payments, categories. Total: 18 tabelas, 34 índices.",
    materialId: "mat-07",
  },
  onboarding: {
    id: "cit-onboarding",
    filename: "onboarding.pdf",
    type: "pdf",
    excerpt:
      "Etapas de onboarding: 1. Clonar repositório. 2. Configurar .env. 3. Rodar docker-compose up. 4. Executar migrations. 5. Popular seeds.",
    materialId: "mat-08",
  },
};

// ─── Mock sprint stories ───────────────────────────────────────────────────────

const SPRINT_STORIES: SprintStory[] = [
  {
    id: "US-24",
    title: "Checkout com PIX",
    description: "Como cliente, quero pagar com PIX para finalizar minha compra de forma rápida e sem taxas adicionais.",
    status: "Em andamento",
    points: 8,
  },
  {
    id: "US-25",
    title: "Notificações de pedido",
    description: "Como cliente, quero receber notificações por e-mail e push sobre o status do meu pedido em tempo real.",
    status: "Concluída",
    points: 5,
  },
  {
    id: "US-26",
    title: "Filtros de catálogo avançados",
    description: "Como usuário, quero filtrar produtos por preço, categoria, avaliação e disponibilidade.",
    status: "A fazer",
    points: 13,
  },
];

// ─── Response builders ─────────────────────────────────────────────────────────

const RESPONSES: Record<Intent, () => AIResponsePayload> = {
  overview: () => ({
    content:
      "O **E-commerce API** é uma plataforma transacional de alto volume construída com arquitetura de microserviços. O sistema processa pedidos, pagamentos e catálogo de forma independente por domínio, garantindo escalabilidade e resiliência.\n\n**Status atual:** Sprint 7 em andamento · Equipe de 6 pessoas · Stack: Node.js, React, PostgreSQL, Kafka, Kong.",
    hasImageCard: true,
    citations: [CITATIONS.readme, CITATIONS.arquitetura],
  }),

  architecture: () => ({
    content:
      "O projeto usa arquitetura de **microserviços** com três camadas principais:\n\n• **Frontend** — React/Next.js para interface do cliente e painel administrativo\n• **API Gateway** — Kong/AWS como ponto centralizado: autenticação, rate limiting e roteamento\n• **Microserviços** — Serviços independentes em Node.js e Python: pedidos, pagamentos, catálogo e usuários\n\nComunicação síncrona via REST e gRPC. Eventos assíncronos via Kafka entre domínios.",
    hasDiagram: true,
    hasImageCard: true,
    citations: [CITATIONS.arquitetura, CITATIONS.readme],
  }),

  sprint: () => ({
    content:
      "O **Sprint 7** está em andamento com 26 pontos comprometidos. A velocidade média da equipe é de 24 pts/sprint. Abaixo as histórias do sprint atual:",
    sprintStories: SPRINT_STORIES,
    citations: [CITATIONS.sprint, CITATIONS.backlog],
  }),

  auth: () => ({
    content:
      "A autenticação usa **JWT com refresh tokens**. O access token expira em 15 minutos; o refresh token dura 7 dias com rotação automática. Os escopos disponíveis são `read`, `write` e `admin`.\n\nClientes públicos (SPAs) usam o fluxo **PKCE** para evitar interceptação do código de autorização. Endpoints protegidos exigem o header `Authorization: Bearer <token>`.",
    citations: [CITATIONS.auth, CITATIONS.swagger],
  }),

  api: () => ({
    content:
      "A API segue o padrão **OpenAPI 3.0** com 47 endpoints documentados em 8 recursos principais: `/users`, `/products`, `/orders`, `/payments`, `/categories`, `/cart`, `/notifications` e `/admin`.\n\nBase path: `/api/v1`. Todos os endpoints retornam JSON com envelope padrão `{ data, meta, errors }`. Rate limiting: 100 req/min por usuário autenticado.",
    citations: [CITATIONS.swagger, CITATIONS.auth],
  }),

  modules: () => ({
    content:
      "O projeto possui **4 microserviços** principais independentes:\n\n• **Order Service** — Gerenciamento de pedidos, estados e histórico (Node.js)\n• **Payment Service** — Integração com PIX, cartão e boleto (Node.js + Stripe)\n• **Catalog Service** — Produtos, categorias, estoque e busca (Python + Elasticsearch)\n• **User Service** — Autenticação, perfis e permissões (Node.js)\n\nCada serviço possui banco de dados próprio (database-per-service pattern).",
    hasDiagram: true,
    citations: [CITATIONS.arquitetura],
  }),

  onboarding: () => ({
    content:
      "Para começar no projeto, siga esta ordem recomendada de leitura:\n\n1. **README.md** — Setup do ambiente local, variáveis de ambiente e scripts\n2. **arquitetura.pdf** — Entender o design do sistema antes de qualquer código\n3. **auth-flow.md** — Fluxo de autenticação usado em todos os serviços\n4. **swagger.yaml** — Contratos da API para entender as integrações\n5. **db-schema.sql** — Estrutura de dados e relacionamentos\n\nAmbiente local sobe via `docker-compose up`. Migrations com `npm run db:migrate`.",
    citations: [CITATIONS.readme, CITATIONS.onboarding, CITATIONS.auth],
  }),

  database: () => ({
    content:
      "O banco de dados principal é **PostgreSQL 15** com 18 tabelas e 34 índices. Tabelas principais:\n\n• `users` + `user_roles` — Identidade e permissões\n• `products` + `categories` + `product_images` — Catálogo\n• `orders` + `order_items` — Pedidos e itens\n• `payments` + `payment_methods` — Transações financeiras\n• `notifications` — Fila de notificações push/email\n\nMigrations gerenciadas com Knex.js. Seeds disponíveis para ambiente de desenvolvimento.",
    citations: [CITATIONS.dbSchema, CITATIONS.arquitetura],
  }),

  default: () => ({
    content:
      "Baseado nos documentos indexados do projeto **E-commerce API**, não encontrei informações específicas sobre esse tema nos materiais disponíveis. Tente reformular a pergunta ou consulte diretamente os arquivos listados no painel de materiais.\n\nSe a informação estiver em um documento ainda não indexado, fale com a equipe de engenharia para incluí-lo na base de conhecimento.",
    citations: [],
  }),
};

// ─── Public API ────────────────────────────────────────────────────────────────

/**
 * Sends a query and returns an AI response payload.
 * Replace this function body with a real API call when the backend is ready.
 */
export async function sendMessage(query: string): Promise<AIResponsePayload> {
  await delay(1600);
  const intent = detectIntent(query);
  return RESPONSES[intent]();
}
