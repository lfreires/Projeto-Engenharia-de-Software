import hashlib
import os
import tempfile
from pathlib import Path
from typing import Protocol

from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from app.config import Settings
from app.schemas import DocumentStatusResponse

CONTENT_TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".txt": "text/plain",
    ".md": "text/markdown",
}


class UnsupportedDocumentType(ValueError):
    pass


class EmptyDocument(ValueError):
    pass


class DeterministicEmbeddings(Embeddings):
    """Local deterministic embeddings used by tests and development without Gemini."""

    def __init__(self, dimensions: int) -> None:
        self._dimensions = dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        values = [0.0] * self._dimensions
        for token in text.lower().split():
            slot = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16) % self._dimensions
            values[slot] += 1.0
        return values


class PrefixedGeminiEmbeddings(Embeddings):
    def __init__(self, settings: Settings) -> None:
        self._delegate = GoogleGenerativeAIEmbeddings(
            model=settings.embedding_model,
            api_key=settings.gemini_api_key,
            output_dimensionality=settings.embedding_dimensions,
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._delegate.embed_documents(
            [f"title: indexed document | text: {text}" for text in texts]
        )

    def embed_document_chunks(self, documents: list[Document]) -> list[list[float]]:
        texts = [
            f"title: {document.metadata['file_name']} | text: {document.page_content}"
            for document in documents
        ]
        return self._delegate.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._delegate.embed_query(f"task: question answering | query: {text}")


class VectorIndex(Protocol):
    def initialize(self) -> None: ...

    def add_documents(self, documents: list[Document], ids: list[str]) -> None: ...

    def delete_documents(self, documents: list[DocumentStatusResponse]) -> None: ...

    def search(self, query: str, project_id: str, top_k: int) -> list[tuple[Document, float]]: ...


class LangChainPGVectorIndex:
    def __init__(self, settings: Settings, embeddings: PrefixedGeminiEmbeddings) -> None:
        self._settings = settings
        self._embeddings = embeddings
        self._store: PGVector | None = None

    def initialize(self) -> None:
        connection = self._settings.database_url.replace(
            "postgresql://", "postgresql+psycopg://", 1
        )
        self._store = PGVector(
            embeddings=self._embeddings,
            connection=connection,
            embedding_length=self._settings.embedding_dimensions,
            collection_name=self._settings.vector_collection_name,
            use_jsonb=True,
            create_extension=False,
            engine_args={"connect_args": {"options": "-csearch_path=public,extensions"}},
        )

    def add_documents(self, documents: list[Document], ids: list[str]) -> None:
        store = self._require_store()
        store.add_embeddings(
            texts=[document.page_content for document in documents],
            embeddings=self._embeddings.embed_document_chunks(documents),
            metadatas=[document.metadata for document in documents],
            ids=ids,
        )

    def delete_documents(self, documents: list[DocumentStatusResponse]) -> None:
        ids = _vector_ids(documents)
        if ids:
            self._require_store().delete(ids=ids)

    def search(self, query: str, project_id: str, top_k: int) -> list[tuple[Document, float]]:
        matches = self._require_store().similarity_search_with_score(
            query,
            k=top_k,
            filter={"project_id": {"$eq": project_id}},
        )
        return [(document, max(0.0, 1.0 - float(distance))) for document, distance in matches]

    def _require_store(self) -> PGVector:
        if self._store is None:
            raise RuntimeError("Vector store has not been initialized.")
        return self._store


class MemoryVectorIndex:
    def __init__(self, embeddings: Embeddings) -> None:
        self._store = InMemoryVectorStore(embeddings)

    def initialize(self) -> None:
        return None

    def add_documents(self, documents: list[Document], ids: list[str]) -> None:
        self._store.add_documents(documents=documents, ids=ids)

    def delete_documents(self, documents: list[DocumentStatusResponse]) -> None:
        ids = _vector_ids(documents)
        if ids:
            self._store.delete(ids=ids)

    def search(self, query: str, project_id: str, top_k: int) -> list[tuple[Document, float]]:
        return self._store.similarity_search_with_score(
            query,
            k=top_k,
            filter=lambda document: document.metadata.get("project_id") == project_id,
        )


def _vector_ids(documents: list[DocumentStatusResponse]) -> list[str]:
    return [
        f"{document.document_id}:{chunk_index}"
        for document in documents
        for chunk_index in range(document.chunk_count)
    ]


def canonical_content_type(file_name: str) -> str:
    extension = Path(file_name).suffix.lower()
    if extension not in CONTENT_TYPES:
        raise UnsupportedDocumentType("Only PDF, DOCX, TXT and MD documents are accepted.")
    return CONTENT_TYPES[extension]


def load_upload(file_name: str, payload: bytes) -> tuple[list[Document], str, str]:
    safe_name = Path(file_name).name
    content_type = canonical_content_type(safe_name)
    extension = Path(safe_name).suffix.lower()
    temporary_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as temporary:
            temporary.write(payload)
            temporary_path = temporary.name
        if extension == ".pdf":
            documents = PyPDFLoader(temporary_path).load()
        elif extension == ".docx":
            documents = Docx2txtLoader(temporary_path).load()
        else:
            documents = TextLoader(temporary_path, encoding="utf-8").load()
    finally:
        if temporary_path:
            os.unlink(temporary_path)
    content = "\n\n".join(
        document.page_content.strip() for document in documents if document.page_content.strip()
    )
    if not content:
        raise EmptyDocument("No extractable text was found in the uploaded document.")
    return documents, content, content_type


def text_document(content: str) -> list[Document]:
    if not content.strip():
        raise EmptyDocument("No extractable text was found in the document.")
    return [Document(page_content=content)]


def split_documents(
    documents: list[Document],
    file_name: str,
    content_type: str,
    settings: Settings,
) -> list[Document]:
    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        add_start_index=True,
    )
    if Path(file_name).suffix.lower() == ".md":
        markdown = "\n\n".join(document.page_content for document in documents)
        header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[("#", "header_1"), ("##", "header_2"), ("###", "header_3")],
            strip_headers=False,
        )
        chunks = recursive_splitter.split_documents(header_splitter.split_text(markdown))
    else:
        chunks = recursive_splitter.split_documents(documents)
    if not chunks:
        raise EmptyDocument("No indexable text was found in the document.")
    return [
        Document(
            page_content=chunk.page_content,
            metadata={
                **chunk.metadata,
                "file_name": file_name,
                "content_type": content_type,
                "chunk_index": index,
            },
        )
        for index, chunk in enumerate(chunks)
    ]
