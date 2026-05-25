import { MaterialType, Project, ProjectMaterial } from "@/models/project";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");
const BEARER_TOKEN = import.meta.env.VITE_BEARER_TOKEN ?? "dev-token";

export const PROJECT_ID: string = import.meta.env.VITE_PROJECT_ID ?? "proj-demo";

interface BackendProject {
  id: string;
  name: string;
  description: string;
}

interface BackendMaterial {
  id: string;
  title: string;
  content_type: string;
  latest_version: {
    document_id: string;
    file_name: string;
    created_at: string;
  };
}

interface BackendDocumentContent {
  content: string;
}

interface BackendUploadResponse {
  document_id: string;
  material_id: string;
  file_name: string;
  status: string;
  chunk_count: number;
}

export class BackendConnectionError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "BackendConnectionError";
  }
}

async function fetchJson<T>(path: string): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { Authorization: `Bearer ${BEARER_TOKEN}` },
    });
  } catch {
    throw new BackendConnectionError("Nao foi possivel conectar ao backend.");
  }

  if (!response.ok) {
    throw new BackendConnectionError(`Backend respondeu com HTTP ${response.status}.`);
  }

  return response.json() as Promise<T>;
}

function inferMaterialType(contentType: string, filename: string): MaterialType {
  const ext = filename.split(".").pop()?.toLowerCase() ?? "";
  if (contentType.includes("pdf") || ext === "pdf") return "pdf";
  if (ext === "docx") return "document";
  if (ext === "txt") return "text";
  if (["xlsx", "xls", "csv"].includes(ext)) return "spreadsheet";
  if (["md", "mdx"].includes(ext)) return "markdown";
  if (ext === "sql") return "sql";
  if (["yaml", "yml"].includes(ext)) return "yaml";
  return "pdf";
}

function mapBackendMaterial(material: BackendMaterial): ProjectMaterial {
  const filename = material.latest_version.file_name;
  return {
    id: material.id,
    documentId: material.latest_version.document_id,
    filename,
    type: inferMaterialType(material.content_type, filename),
    label: material.title,
    description: material.title,
    size: "-",
    lastUpdated: new Date(material.latest_version.created_at).toLocaleDateString("pt-BR"),
    tags: [],
  };
}

export async function fetchProject(projectId: string = PROJECT_ID): Promise<Project> {
  const data = await fetchJson<BackendProject>(`/api/v1/projects/${projectId}`);
  return {
    id: data.id,
    name: data.name,
    description: data.description,
    stack: [],
    currentSprint: 0,
    teamSize: 0,
    status: "Em andamento",
    materials: [],
  };
}

export async function fetchProjectMaterials(
  projectId: string = PROJECT_ID,
): Promise<ProjectMaterial[]> {
  const data = await fetchJson<{ materials: BackendMaterial[] }>(
    `/api/v1/projects/${projectId}/materials`,
  );
  return data.materials.map(mapBackendMaterial);
}

export async function fetchDocumentContent(documentId: string): Promise<string> {
  const data = await fetchJson<BackendDocumentContent>(
    `/api/v1/ingestion/documents/${documentId}/content`,
  );
  return data.content;
}

export async function uploadProjectDocument(
  file: File,
  projectId: string = PROJECT_ID,
): Promise<BackendUploadResponse> {
  const form = new FormData();
  form.append("project_id", projectId);
  form.append("file", file);
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/v1/ingestion/uploads`, {
      method: "POST",
      headers: { Authorization: `Bearer ${BEARER_TOKEN}` },
      body: form,
    });
  } catch {
    throw new BackendConnectionError("Nao foi possivel conectar ao backend.");
  }
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    const message = payload?.detail?.message ?? `Backend respondeu com HTTP ${response.status}.`;
    throw new BackendConnectionError(message);
  }
  return response.json() as Promise<BackendUploadResponse>;
}
