import { ThumbsUp, ThumbsDown } from "lucide-react";
import { FeedbackRating } from "@/models/message";

interface FeedbackButtonsProps {
  messageId: string;
  currentFeedback?: FeedbackRating;
  onFeedback: (messageId: string, rating: FeedbackRating) => void;
}

export function FeedbackButtons({ messageId, currentFeedback, onFeedback }: FeedbackButtonsProps) {
  const isPositive = currentFeedback === "positive";
  const isNegative = currentFeedback === "negative";

  const baseStyle: React.CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    width: 26,
    height: 26,
    borderRadius: 6,
    border: "0.5px solid",
    cursor: currentFeedback ? "default" : "pointer",
    transition: "all 0.15s ease",
  };

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 6,
        marginTop: 8,
      }}
    >
      <span
        style={{
          fontSize: "10px",
          color: "#6b7080",
          fontWeight: 500,
          marginRight: 2,
          userSelect: "none",
        }}
      >
        Esta resposta foi útil?
      </span>

      {/* Thumbs up */}
      <button
        onClick={() => !currentFeedback && onFeedback(messageId, "positive")}
        title="Resposta útil"
        style={{
          ...baseStyle,
          backgroundColor: isPositive ? "rgba(34, 197, 94, 0.15)" : "#14171f",
          borderColor: isPositive ? "rgba(34, 197, 94, 0.5)" : "#232733",
          color: isPositive ? "#86efac" : "#6b7080",
        }}
      >
        <ThumbsUp size={12} fill={isPositive ? "#86efac" : "none"} />
      </button>

      {/* Thumbs down */}
      <button
        onClick={() => !currentFeedback && onFeedback(messageId, "negative")}
        title="Resposta não útil"
        style={{
          ...baseStyle,
          backgroundColor: isNegative ? "rgba(239, 68, 68, 0.15)" : "#14171f",
          borderColor: isNegative ? "rgba(239, 68, 68, 0.5)" : "#232733",
          color: isNegative ? "#fca5a5" : "#6b7080",
        }}
      >
        <ThumbsDown size={12} fill={isNegative ? "#fca5a5" : "none"} />
      </button>

      {/* Confirmation label after rating */}
      {currentFeedback && (
        <span
          style={{
            fontSize: "10px",
            color: currentFeedback === "positive" ? "#86efac" : "#fca5a5",
            fontWeight: 500,
          }}
        >
          {currentFeedback === "positive" ? "Obrigado!" : "Feedback enviado"}
        </span>
      )}
    </div>
  );
}
