from app.dependencies import get_ingestion_service
from app.domain.models import IndexedChunk, IndexedDocument
from app.services.chunker import TextChunker


def reset_index() -> None:
    get_ingestion_service().reset()


def chunk_text(content: str, max_words: int = 180) -> list[str]:
    return TextChunker(max_words=max_words).split(content, max_words=max_words)


def index_document(
    project_id: str,
    material_id: str,
    file_name: str,
    content: str,
) -> IndexedDocument:
    return get_ingestion_service().index_document(project_id, material_id, file_name, content)


def get_document(document_id: str) -> IndexedDocument | None:
    try:
        return get_ingestion_service().get_document_status(document_id)
    except Exception:
        return None


def search_chunks(project_id: str, query: str, top_k: int) -> list[IndexedChunk]:
    return get_ingestion_service().search(project_id=project_id, query=query, top_k=top_k)
