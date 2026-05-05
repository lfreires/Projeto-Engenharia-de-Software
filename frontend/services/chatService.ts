import { AIResponsePayload } from "@/models/chat";
import { CitationSource } from "@/models/citation";
import { MaterialType } from "@/models/project";

// ─── Config ───────────────────────────────────────────────────────────────────

const API_BASE = "/api/v1/query";
const BEARER_TOKEN = import.meta.env.VITE_BEARER_TOKEN ?? "dev-token";

// ─── Backend response shape (mirrors backend ChatResponse) ────────────────────

interface BackendSource {
  document_id: string;
  file_name: string;
  chunk_index: number;
  score: number;
}

interface BackendChatResponse {
  session_id: string;
  answer: string;
  model_used: string;
  sources: BackendSource[];
  latency_ms: number;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function inferMaterialType(filename: string): MaterialType {
  const ext = filename.split(".").pop()?.toLowerCase() ?? "";
  if (ext === "pdf") return "pdf";
  if (["xlsx", "xls", "csv"].includes(ext)) return "spreadsheet";
  if (["md", "mdx"].includes(ext)) return "markdown";
  if (ext === "sql") return "sql";
  if (["yaml", "yml"].includes(ext)) return "yaml";
  return "pdf";
}

function mapSourcesToCitations(sources: BackendSource[]): CitationSource[] {
  return sources.map((s) => ({
    id: s.document_id,
    filename: s.file_name,
    type: inferMaterialType(s.file_name),
    excerpt: `Relevância: ${(s.score * 100).toFixed(0)}% — chunk #${s.chunk_index}`,
    materialId: s.document_id,
  }));
}

function errorMessage(status: number): string {
  switch (status) {
    case 401: return "Sessão expirada. Recarregue a página e tente novamente.";
    case 404: return "Nenhum documento indexado encontrado para este projeto.";
    case 429: return "Limite de requisições atingido. Aguarde alguns instantes e tente novamente.";
    case 503: return "O serviço de IA está temporariamente indisponível. Tente novamente em instantes.";
    default:  return "Não foi possível processar sua pergunta no momento. Tente novamente.";
  }
}

// ─── Public API ────────────────────────────────────────────────────────────────

/**
 * Sends a question to the RAG backend and returns an AIResponsePayload.
 *
 * @param message  - The user's question
 * @param projectId - The project being queried (VITE_PROJECT_ID or fallback)
 * @param sessionId - Session UUID managed by useChat
 */
export async function sendMessage(
  message: string,
  projectId: string,
  sessionId: string,
): Promise<AIResponsePayload> {
  const resp = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${BEARER_TOKEN}`,
    },
    body: JSON.stringify({ project_id: projectId, session_id: sessionId, message, top_k: 5 }),
  });

  if (!resp.ok) {
    throw new Error(errorMessage(resp.status));
  }

  const data: BackendChatResponse = await resp.json();

  return {
    content: data.answer,
    citations: mapSourcesToCitations(data.sources),
  };
}

/**
 * Clears the session history on the backend.
 */
export async function clearSession(sessionId: string): Promise<void> {
  await fetch(`${API_BASE}/history/${sessionId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${BEARER_TOKEN}` },
  });
}

/**
 * Sends thumbs up/down feedback for an AI message.
 */
export async function sendFeedback(
  sessionId: string,
  messageId: string,
  rating: "positive" | "negative",
  comment?: string,
): Promise<void> {
  await fetch(`${API_BASE}/feedback`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${BEARER_TOKEN}`,
    },
    body: JSON.stringify({ session_id: sessionId, message_id: messageId, rating, comment }),
  });
}
