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

export class BackendConnectionError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "BackendConnectionError";
  }
}

function requireApiBaseUrl(): string {
  if (!API_BASE_URL) {
    throw new BackendConnectionError("VITE_API_BASE_URL nao foi configurada.");
  }
  return API_BASE_URL;
}

async function fetchJson<T>(path: string): Promise<T> {
  const baseUrl = requireApiBaseUrl();
  let response: Response;

  try {
    response = await fetch(`${baseUrl}${path}`, {
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
    filename,
    type: inferMaterialType(material.content_type, filename),
    label: material.title,
    description: `Documento ${material.latest_version.document_id}`,
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
