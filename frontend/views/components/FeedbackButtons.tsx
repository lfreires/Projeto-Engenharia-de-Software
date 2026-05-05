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
          color: "#b0b5c8",
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
          backgroundColor: isPositive ? "#ecfdf5" : "#f8f9fc",
          borderColor: isPositive ? "#6ee7b7" : "#e5e7ef",
          color: isPositive ? "#059669" : "#9ca3af",
        }}
      >
        <ThumbsUp size={12} fill={isPositive ? "#059669" : "none"} />
      </button>

      {/* Thumbs down */}
      <button
        onClick={() => !currentFeedback && onFeedback(messageId, "negative")}
        title="Resposta não útil"
        style={{
          ...baseStyle,
          backgroundColor: isNegative ? "#fff1f2" : "#f8f9fc",
          borderColor: isNegative ? "#fca5a5" : "#e5e7ef",
          color: isNegative ? "#dc2626" : "#9ca3af",
        }}
      >
        <ThumbsDown size={12} fill={isNegative ? "#dc2626" : "none"} />
      </button>

      {/* Confirmation label after rating */}
      {currentFeedback && (
        <span
          style={{
            fontSize: "10px",
            color: currentFeedback === "positive" ? "#059669" : "#dc2626",
            fontWeight: 500,
          }}
        >
          {currentFeedback === "positive" ? "Obrigado!" : "Feedback enviado"}
        </span>
      )}
    </div>
  );
}
