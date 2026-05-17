from functools import lru_cache

from app.config import settings
from app.repositories.document_index import InMemoryDocumentIndex
from app.services.chunker import TextChunker
from app.services.ingestion_service import IngestionService
from app.services.token_validator import TokenValidator


@lru_cache
def get_ingestion_service() -> IngestionService:
    chunker = TextChunker(max_words=settings.default_chunk_max_words)
    return IngestionService(index=InMemoryDocumentIndex(chunker=chunker))


@lru_cache
def get_token_validator() -> TokenValidator:
    return TokenValidator()
