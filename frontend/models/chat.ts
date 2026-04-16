import { CitationSource } from "./citation";
import { SprintStory } from "./project";

export interface AIResponsePayload {
  content: string;
  citations?: CitationSource[];
  hasDiagram?: boolean;
  hasImageCard?: boolean;
  sprintStories?: SprintStory[];
}
