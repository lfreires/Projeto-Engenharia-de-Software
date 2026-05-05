from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    project_id: str = Field(..., description="UUID do projeto")
    session_id: str = Field(..., description="UUID da sessão de chat")
    message: str = Field(..., min_length=1, max_length=2000, description="Pergunta do usuário")
    top_k: int = Field(default=5, ge=1, le=20, description="Chunks a recuperar")


class SourceItem(BaseModel):
    document_id: str
    file_name: str
    chunk_index: int
    score: float


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    model_used: str
    sources: list[SourceItem]
    latency_ms: int


class HistoryTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HistoryResponse(BaseModel):
    session_id: str
    turns: list[HistoryTurn]


class FeedbackRequest(BaseModel):
    session_id: str = Field(..., description="UUID da sessão")
    message_id: str = Field(..., description="ID da mensagem avaliada")
    rating: Literal["positive", "negative"] = Field(..., description="Avaliação do usuário")
    comment: str | None = Field(default=None, max_length=500, description="Comentário opcional")


class FeedbackResponse(BaseModel):
    accepted: bool
    message_id: str
