from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class TokenValidationRequest(BaseModel):
    token: str = Field(..., min_length=1)
    project_id: str | None = None


class TokenValidationResponse(BaseModel):
    active: bool
    subject_id: str
    subject_type: str
    project_id: str | None
    permissions: list[str]


class UserItem(BaseModel):
    id: str
    email: str
    display_name: str


class UsersResponse(BaseModel):
    users: list[UserItem]


class MembershipItem(BaseModel):
    project_id: str
    user_id: str
    role: str
    permissions: list[str]


class MembershipsResponse(BaseModel):
    memberships: list[MembershipItem]


class Project(BaseModel):
    id: str
    name: str
    description: str
    created_at: datetime


class MaterialVersion(BaseModel):
    id: str
    material_id: str
    version: int
    document_id: str
    file_name: str
    created_at: datetime


class Material(BaseModel):
    id: str
    project_id: str
    title: str
    content_type: str
    latest_version: MaterialVersion


class ProjectsResponse(BaseModel):
    projects: list[Project]


class MaterialsResponse(BaseModel):
    materials: list[Material]


class DocumentCreateRequest(BaseModel):
    project_id: str = Field(..., min_length=1)
    material_id: str = Field(..., min_length=1)
    file_name: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)


class DocumentStatusResponse(BaseModel):
    document_id: str
    project_id: str
    material_id: str
    file_name: str
    status: str
    chunk_count: int


class DocumentContentResponse(DocumentStatusResponse):
    content: str


class SearchRequest(BaseModel):
    project_id: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class SearchChunk(BaseModel):
    document_id: str
    project_id: str
    material_id: str
    file_name: str
    location: str
    chunk_index: int
    chunk_text: str
    score: float


class SearchResponse(BaseModel):
    chunks: list[SearchChunk]


class ChatRequest(BaseModel):
    project_id: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)


class SourceItem(BaseModel):
    document_id: str
    material_id: str | None = None
    file_name: str
    location: str | None = None
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
    session_id: str = Field(..., min_length=1)
    message_id: str = Field(..., min_length=1)
    rating: Literal["positive", "negative"]
    comment: str | None = Field(default=None, max_length=500)


class FeedbackResponse(BaseModel):
    accepted: bool
    message_id: str
