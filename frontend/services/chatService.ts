import { AIResponsePayload } from "@/models/chat";
import { CitationSource } from "@/models/citation";
import { MaterialType } from "@/models/project";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");
const API_BASE = `${API_BASE_URL}/api/v1/query`;
const BEARER_TOKEN = import.meta.env.VITE_BEARER_TOKEN ?? "dev-token";

interface BackendSource {
  document_id: string;
  material_id?: string | null;
  file_name: string;
  location?: string | null;
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

function inferMaterialType(filename: string): MaterialType {
  const ext = filename.split(".").pop()?.toLowerCase() ?? "";
  if (ext === "pdf") return "pdf";
  if (ext === "docx") return "document";
  if (ext === "txt") return "text";
  if (["xlsx", "xls", "csv"].includes(ext)) return "spreadsheet";
  if (["md", "mdx"].includes(ext)) return "markdown";
  if (ext === "sql") return "sql";
  if (["yaml", "yml"].includes(ext)) return "yaml";
  return "pdf";
}

function mapSourcesToCitations(sources: BackendSource[]): CitationSource[] {
  return sources.map((source) => {
    return {
      id: source.document_id,
      filename: source.file_name,
      type: inferMaterialType(source.file_name),
      excerpt: "Documento utilizado para fundamentar esta resposta.",
      materialId: source.material_id ?? source.document_id,
    };
  });
}

function errorMessage(status: number): string {
  switch (status) {
    case 401:
      return "Sessao expirada. Recarregue a pagina e tente novamente.";
    case 404:
      return "Envie um documento em Materiais antes de fazer perguntas.";
    case 429:
      return "Limite de requisicoes atingido. Aguarde alguns instantes e tente novamente.";
    case 503:
      return "O servico de IA esta temporariamente indisponivel.";
    default:
      return "Nao foi possivel processar sua pergunta no momento.";
  }
}

export async function sendMessage(
  message: string,
  projectId: string,
  sessionId: string,
): Promise<AIResponsePayload> {
  let resp: Response;
  try {
    resp = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${BEARER_TOKEN}`,
      },
      body: JSON.stringify({ project_id: projectId, session_id: sessionId, message, top_k: 5 }),
    });
  } catch {
    throw new Error("Nao foi possivel conectar ao backend.");
  }

  if (!resp.ok) {
    throw new Error(errorMessage(resp.status));
  }

  const data: BackendChatResponse = await resp.json();
  return {
    content: data.answer,
    citations: mapSourcesToCitations(data.sources),
  };
}

export async function clearSession(sessionId: string): Promise<void> {
  await fetch(`${API_BASE}/history/${sessionId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${BEARER_TOKEN}` },
  });
}

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
