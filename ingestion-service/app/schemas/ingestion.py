from pydantic import BaseModel, Field


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
