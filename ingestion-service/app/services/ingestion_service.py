from app.domain.models import IndexedChunk, IndexedDocument
from app.repositories.document_index import DocumentIndex


class DocumentNotFoundError(Exception):
    pass


class IngestionService:
    def __init__(self, index: DocumentIndex) -> None:
        self._index = index

    def reset(self) -> None:
        self._index.reset()

    def index_document(
        self,
        project_id: str,
        material_id: str,
        file_name: str,
        content: str,
    ) -> IndexedDocument:
        return self._index.index_document(
            project_id=project_id,
            material_id=material_id,
            file_name=file_name,
            content=content,
        )

    def get_document_status(self, document_id: str) -> IndexedDocument:
        document = self._index.get_document(document_id)
        if document is None:
            raise DocumentNotFoundError()
        return document

    def search(self, project_id: str, query: str, top_k: int) -> list[IndexedChunk]:
        return self._index.search(project_id=project_id, query=query, top_k=top_k)
