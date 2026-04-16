import React from "react";

export type MessageRole = "ai" | "user";

export interface Message {
  id: string;
  role: MessageRole;
  content: string | React.ReactNode;
  citation?: string;
  hasDiagram?: boolean;
  timestamp: Date;
}
