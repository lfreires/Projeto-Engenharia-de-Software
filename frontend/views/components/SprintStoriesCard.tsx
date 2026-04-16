import React from "react";
import { SprintStory, StoryStatus } from "@/models/project";

const STATUS_CONFIG: Record<StoryStatus, { label: string; color: string; bg: string; border: string }> = {
  "Em andamento": { label: "Em andamento", color: "#a16207", bg: "#fefce8", border: "#fde68a" },
  "Concluída":    { label: "Concluída",    color: "#166534", bg: "#f0fdf4", border: "#bbf7d0" },
  "A fazer":      { label: "A fazer",      color: "#6b7280", bg: "#f8f9fc", border: "#e5e7eb" },
};

interface SprintStoriesCardProps {
  stories: SprintStory[];
}

export function SprintStoriesCard({ stories }: SprintStoriesCardProps) {
  return (
    <div className="mt-3" style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
      {stories.map((story) => {
        const status = STATUS_CONFIG[story.status];
        return (
          <div
            key={story.id}
            style={{
              borderRadius: "8px",
              border: "0.5px solid #e5e8f0",
              backgroundColor: "#fafbff",
              padding: "10px 12px",
            }}
          >
            <div
              style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "5px", flexWrap: "wrap" }}
            >
              <span
                style={{
                  fontSize: "10px",
                  fontWeight: 700,
                  backgroundColor: "#eef2ff",
                  color: "#4338ca",
                  borderRadius: "4px",
                  padding: "1px 6px",
                }}
              >
                {story.id}
              </span>

              <span style={{ fontSize: "13px", fontWeight: 600, color: "#1e2035", flex: 1 }}>
                {story.title}
              </span>

              <div style={{ display: "flex", alignItems: "center", gap: "5px", marginLeft: "auto" }}>
                <span
                  style={{
                    fontSize: "10px",
                    fontWeight: 500,
                    padding: "2px 8px",
                    borderRadius: "9999px",
                    backgroundColor: status.bg,
                    color: status.color,
                    border: `0.5px solid ${status.border}`,
                  }}
                >
                  {status.label}
                </span>
                <span
                  style={{
                    fontSize: "10px",
                    color: "#a0a4b8",
                    backgroundColor: "#f3f4f9",
                    padding: "2px 6px",
                    borderRadius: "4px",
                  }}
                >
                  {story.points} pts
                </span>
              </div>
            </div>

            <p style={{ fontSize: "12px", color: "#6b7080", lineHeight: "1.5", margin: 0 }}>
              {story.description}
            </p>
          </div>
        );
      })}
    </div>
  );
}
