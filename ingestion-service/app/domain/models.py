from dataclasses import dataclass


@dataclass(frozen=True)
class IndexedDocument:
    document_id: str
    project_id: str
    material_id: str
    file_name: str
    status: str
    chunk_count: int


@dataclass(frozen=True)
class IndexedChunk:
    document_id: str
    project_id: str
    material_id: str
    file_name: str
    location: str
    chunk_index: int
    chunk_text: str
    score: float = 0.0
