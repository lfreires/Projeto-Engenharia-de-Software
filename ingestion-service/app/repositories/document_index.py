import re
from itertools import count
from typing import Protocol

from app.domain.models import IndexedChunk, IndexedDocument
from app.services.chunker import TextChunker


class DocumentIndex(Protocol):
    def reset(self) -> None:
        raise NotImplementedError

    def index_document(
        self,
        project_id: str,
        material_id: str,
        file_name: str,
        content: str,
    ) -> IndexedDocument:
        raise NotImplementedError

    def get_document(self, document_id: str) -> IndexedDocument | None:
        raise NotImplementedError

    def search(self, project_id: str, query: str, top_k: int) -> list[IndexedChunk]:
        raise NotImplementedError


class InMemoryDocumentIndex:
    def __init__(self, chunker: TextChunker) -> None:
        self._chunker = chunker
        self._document_counter = count(1)
        self._documents: dict[str, IndexedDocument] = {}
        self._chunks: list[IndexedChunk] = []

    def reset(self) -> None:
        self._document_counter = count(1)
        self._documents.clear()
        self._chunks.clear()

    def index_document(
        self,
        project_id: str,
        material_id: str,
        file_name: str,
        content: str,
    ) -> IndexedDocument:
        document_id = f"doc-{next(self._document_counter)}"
        chunks = self._chunker.split(content)
        document = IndexedDocument(
            document_id=document_id,
            project_id=project_id,
            material_id=material_id,
            file_name=file_name,
            status="indexed",
            chunk_count=len(chunks),
        )
        self._documents[document_id] = document

        for chunk_index, chunk in enumerate(chunks):
            self._chunks.append(
                IndexedChunk(
                    document_id=document_id,
                    project_id=project_id,
                    material_id=material_id,
                    file_name=file_name,
                    location=f"{file_name}#chunk-{chunk_index}",
                    chunk_index=chunk_index,
                    chunk_text=chunk,
                )
            )

        return document

    def get_document(self, document_id: str) -> IndexedDocument | None:
        return self._documents.get(document_id)

    def search(self, project_id: str, query: str, top_k: int) -> list[IndexedChunk]:
        query_tokens = self._tokens(query)
        ranked: list[IndexedChunk] = []

        for chunk in self._chunks:
            if chunk.project_id != project_id:
                continue
            score = len(query_tokens.intersection(self._tokens(chunk.chunk_text)))
            if score <= 0:
                continue
            ranked.append(
                IndexedChunk(
                    document_id=chunk.document_id,
                    project_id=chunk.project_id,
                    material_id=chunk.material_id,
                    file_name=chunk.file_name,
                    location=chunk.location,
                    chunk_index=chunk.chunk_index,
                    chunk_text=chunk.chunk_text,
                    score=float(score),
                )
            )

        ranked.sort(key=lambda item: item.score, reverse=True)
        return ranked[:top_k]

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return set(re.findall(r"[a-z0-9]+", text.lower()))
