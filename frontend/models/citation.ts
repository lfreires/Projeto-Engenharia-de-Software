import { MaterialType } from "./project";

export interface CitationSource {
  id: string;
  filename: string;
  type: MaterialType;
  excerpt: string;
  materialId: string;
}
