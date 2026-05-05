import { CitationSource } from "./citation";
import { SprintStory } from "./project";

export type MessageRole = "ai" | "user";

export type FeedbackRating = "positive" | "negative";

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  citations?: CitationSource[];
  hasDiagram?: boolean;
  hasImageCard?: boolean;
  sprintStories?: SprintStory[];
  isError?: boolean;
  timestamp: Date;
  feedback?: FeedbackRating;
}
