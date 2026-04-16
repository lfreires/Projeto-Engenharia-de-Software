export type MaterialType = "pdf" | "spreadsheet" | "markdown" | "sql" | "yaml" | "diagram";

export type ProjectStatus = "Em andamento" | "Concluído" | "Pausado";

export type StoryStatus = "Em andamento" | "Concluída" | "A fazer";

export interface SprintStory {
  id: string;
  title: string;
  description: string;
  status: StoryStatus;
  points: number;
}

export interface ProjectMaterial {
  id: string;
  filename: string;
  type: MaterialType;
  label: string;
  description: string;
  size: string;
  lastUpdated: string;
  tags: string[];
}

export interface Project {
  id: string;
  name: string;
  description: string;
  stack: string[];
  currentSprint: number;
  teamSize: number;
  status: ProjectStatus;
  materials: ProjectMaterial[];
}
