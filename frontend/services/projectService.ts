import { Project, ProjectMaterial } from "@/models/project";

// ─── Config ───────────────────────────────────────────────────────────────────

/**
 * The active project ID comes from the build-time env var VITE_PROJECT_ID.
 * Set it in .env.local to match the project_id used when documents were indexed.
 * Default matches the demo project used during development.
 */
export const PROJECT_ID: string = import.meta.env.VITE_PROJECT_ID ?? "ecommerce-api";

// ─── Static project metadata ──────────────────────────────────────────────────
// This data describes the project shell shown in the UI (header, sidebar).
// The actual document content lives in Azure AI Search (indexed by the Ingestion module).
// Update these values to reflect your real project.

const MATERIALS: ProjectMaterial[] = [
  {
    id: "mat-01",
    filename: "arquitetura.pdf",
    type: "pdf",
    label: "Documento de Arquitetura",
    description: "Visão geral da arquitetura de microserviços, decisões técnicas e diagramas de componentes.",
    size: "2.4 MB",
    lastUpdated: "há 3 dias",
    tags: ["arquitetura", "microserviços", "design"],
  },
  {
    id: "mat-02",
    filename: "swagger.yaml",
    type: "yaml",
    label: "Documentação da API",
    description: "Especificação OpenAPI 3.0 com todos os endpoints, schemas e exemplos de requisição.",
    size: "148 KB",
    lastUpdated: "há 1 dia",
    tags: ["api", "endpoints", "swagger"],
  },
  {
    id: "mat-03",
    filename: "sprint7-ata.xlsx",
    type: "spreadsheet",
    label: "Ata do Sprint 7",
    description: "Histórias de usuário, pontuação, responsáveis e status do sprint atual.",
    size: "84 KB",
    lastUpdated: "há 2 dias",
    tags: ["sprint", "backlog", "scrum"],
  },
  {
    id: "mat-04",
    filename: "README.md",
    type: "markdown",
    label: "README do Projeto",
    description: "Instruções de setup, variáveis de ambiente, scripts disponíveis e links úteis.",
    size: "22 KB",
    lastUpdated: "há 5 dias",
    tags: ["onboarding", "setup", "docs"],
  },
  {
    id: "mat-05",
    filename: "auth-flow.md",
    type: "markdown",
    label: "Fluxo de Autenticação",
    description: "Documentação do fluxo JWT com refresh tokens, escopos e políticas de acesso.",
    size: "18 KB",
    lastUpdated: "há 7 dias",
    tags: ["auth", "jwt", "segurança"],
  },
  {
    id: "mat-06",
    filename: "backlog.xlsx",
    type: "spreadsheet",
    label: "Backlog do Produto",
    description: "Lista completa de funcionalidades planejadas, priorizadas por valor de negócio.",
    size: "210 KB",
    lastUpdated: "há 4 dias",
    tags: ["backlog", "produto", "planejamento"],
  },
  {
    id: "mat-07",
    filename: "db-schema.sql",
    type: "sql",
    label: "Schema do Banco de Dados",
    description: "DDL do PostgreSQL com todas as tabelas, índices, constraints e relacionamentos.",
    size: "56 KB",
    lastUpdated: "há 6 dias",
    tags: ["database", "sql", "schema"],
  },
  {
    id: "mat-08",
    filename: "onboarding.pdf",
    type: "pdf",
    label: "Guia de Onboarding",
    description: "Guia técnico para novos membros da equipe: ambiente, padrões de código e fluxo de trabalho.",
    size: "1.1 MB",
    lastUpdated: "há 10 dias",
    tags: ["onboarding", "equipe", "padrões"],
  },
];

export const CURRENT_PROJECT: Project = {
  id: PROJECT_ID,
  name: "E-commerce API",
  description: "Plataforma de e-commerce com arquitetura de microserviços para alto volume transacional.",
  stack: ["Node.js", "React", "PostgreSQL", "Kafka", "Kong"],
  currentSprint: 7,
  teamSize: 6,
  status: "Em andamento",
  materials: MATERIALS,
};

export function getCurrentProject(): Project {
  return CURRENT_PROJECT;
}

export function getMaterialById(id: string): ProjectMaterial | undefined {
  return MATERIALS.find((m) => m.id === id);
}
