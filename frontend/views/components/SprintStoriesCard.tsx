import React from "react";
import { SprintStory, StoryStatus } from "@/models/project";

const STATUS_CONFIG: Record<StoryStatus, { label: string; color: string; bg: string; border: string }> = {
  "Em andamento": { label: "Em andamento", color: "#fcd34d", bg: "rgba(202, 138, 4, 0.18)",   border: "rgba(202, 138, 4, 0.4)"   },
  "Concluída":    { label: "Concluída",    color: "#86efac", bg: "rgba(34, 197, 94, 0.18)",   border: "rgba(34, 197, 94, 0.4)"   },
  "A fazer":      { label: "A fazer",      color: "#a1a6b8", bg: "rgba(148, 163, 184, 0.15)", border: "rgba(148, 163, 184, 0.35)"},
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
              border: "0.5px solid #232733",
              backgroundColor: "#14171f",
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
                  backgroundColor: "rgba(99, 102, 241, 0.18)",
                  color: "#a5b4fc",
                  borderRadius: "4px",
                  padding: "1px 6px",
                }}
              >
                {story.id}
              </span>

              <span style={{ fontSize: "13px", fontWeight: 600, color: "#e6e8ee", flex: 1 }}>
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
                    color: "#8b90a5",
                    backgroundColor: "#1a1d25",
                    padding: "2px 6px",
                    borderRadius: "4px",
                  }}
                >
                  {story.points} pts
                </span>
              </div>
            </div>

            <p style={{ fontSize: "12px", color: "#a1a6b8", lineHeight: "1.5", margin: 0 }}>
              {story.description}
            </p>
          </div>
        );
      })}
    </div>
  );
}
