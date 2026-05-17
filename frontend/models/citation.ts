import { MaterialType } from "./project";

export interface CitationSource {
  id: string;
  filename: string;
  location?: string;
  type: MaterialType;
  excerpt: string;
  materialId: string;
}
