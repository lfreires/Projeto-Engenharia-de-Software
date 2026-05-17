from app.domain.models import IndexedChunk
from app.services.ingestion_service import IngestionService


class Retriever:
    def __init__(self, service: IngestionService) -> None:
        self._service = service

    def retrieve(self, query: str, project_id: str, top_k: int) -> list[IndexedChunk]:
        return self._service.search(project_id=project_id, query=query, top_k=top_k)
