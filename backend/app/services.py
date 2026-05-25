import hashlib
import time
from dataclasses import dataclass
from pathlib import Path

from fastapi import HTTPException, status

from app.config import Settings
from app.rag import (
    EmptyDocument,
    UnsupportedDocumentType,
    VectorIndex,
    canonical_content_type,
    load_upload,
    split_documents,
    text_document,
)
from app.schemas import (
    ChatRequest,
    ChatResponse,
    DocumentContentResponse,
    DocumentCreateRequest,
    DocumentStatusResponse,
    FeedbackRequest,
    FeedbackResponse,
    HistoryResponse,
    MaterialsResponse,
    MembershipsResponse,
    ProjectsResponse,
    SearchChunk,
    SearchRequest,
    SearchResponse,
    SourceItem,
    TokenValidationResponse,
    UsersResponse,
)
from app.storage import Store, content_digest


@dataclass
class Services:
    settings: Settings
    store: Store
    vector_index: VectorIndex
    chat_client: object

    def initialize(self) -> None:
        self.vector_index.initialize()

    def validate_identity_token(
        self, token: str, project_id: str | None
    ) -> TokenValidationResponse:
        base_validation = self.store.validate_token(token, None)
        if base_validation is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_TOKEN", "message": "Token is invalid or inactive."},
            )
        validation = self.store.validate_token(token, project_id)
        if validation is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "PROJECT_FORBIDDEN",
                    "message": "Token subject is not a member of this project.",
                },
            )
        return validation

    def authorize(self, token: str, project_id: str | None = None) -> None:
        if self.store.validate_token(token, project_id) is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "UNAUTHORIZED", "message": "Invalid or missing Bearer token"},
            )

    async def seed(self) -> None:
        self.store.seed_catalog_and_identity(
            self.settings.bearer_token,
            self.settings.internal_service_token,
        )

    def list_users(self) -> UsersResponse:
        return UsersResponse(users=self.store.list_users())

    def list_memberships(self, project_id: str | None) -> MembershipsResponse:
        return MembershipsResponse(memberships=self.store.list_memberships(project_id))

    def list_projects(self) -> ProjectsResponse:
        return ProjectsResponse(projects=self.store.list_projects())

    def get_project(self, project_id: str):
        project = self.store.get_project(project_id)
        if project is None:
            _project_not_found()
        return project

    def list_materials(self, project_id: str) -> MaterialsResponse:
        self.get_project(project_id)
        return MaterialsResponse(materials=self.store.list_materials(project_id))

    async def upload_document(
        self, project_id: str, file_name: str, payload: bytes
    ) -> DocumentStatusResponse:
        if self.store.get_project(project_id) is None:
            _project_not_found()
        safe_name = Path(file_name).name
        if not safe_name:
            _invalid_document("A file name is required.")
        content_type = self._validate_upload(safe_name, payload)
        document = self.store.create_upload_document(
            project_id=project_id,
            title=Path(safe_name).stem,
            file_name=safe_name,
            content_type=content_type,
            content_hash=hashlib.sha256(payload).hexdigest(),
        )
        try:
            source_documents, content, _ = load_upload(safe_name, payload)
        except EmptyDocument as exc:
            self.store.mark_document_failed(document.document_id, str(exc))
            _invalid_document(str(exc))
        except Exception as exc:
            self.store.mark_document_failed(document.document_id, str(exc))
            _invalid_document("The uploaded document could not be read.")
        return self._index_loaded(document, source_documents, content)

    async def index_document(self, request: DocumentCreateRequest) -> DocumentStatusResponse:
        if self.store.get_project(request.project_id) is None:
            _project_not_found()
        if not self.store.has_material(request.project_id, request.material_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "MATERIAL_NOT_FOUND", "message": "Material not found."},
            )
        try:
            content_type = canonical_content_type(request.file_name)
        except UnsupportedDocumentType as exc:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail={"code": "UNSUPPORTED_DOCUMENT_TYPE", "message": str(exc)},
            ) from exc
        digest = content_digest(request.content)
        existing = self.store.get_document_by_hash(request.project_id, request.material_id, digest)
        if existing:
            return existing
        document = self.store.create_document_version(
            request.project_id,
            request.material_id,
            Path(request.file_name).name,
            content_type,
            digest,
        )
        try:
            source_documents = text_document(request.content)
        except EmptyDocument as exc:
            self.store.mark_document_failed(document.document_id, str(exc))
            _invalid_document(str(exc))
        return self._index_loaded(document, source_documents, request.content)

    def _validate_upload(self, file_name: str, payload: bytes) -> str:
        try:
            content_type = canonical_content_type(file_name)
        except UnsupportedDocumentType as exc:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail={"code": "UNSUPPORTED_DOCUMENT_TYPE", "message": str(exc)},
            ) from exc
        if len(payload) > self.settings.max_upload_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail={"code": "FILE_TOO_LARGE", "message": "Maximum file size is 10 MB."},
            )
        if not payload:
            _invalid_document("The uploaded document is empty.")
        return content_type

    def _index_loaded(
        self, document: DocumentStatusResponse, source_documents: list, content: str
    ) -> DocumentStatusResponse:
        try:
            chunks = split_documents(
                source_documents, document.file_name, document.content_type, self.settings
            )
            for chunk in chunks:
                chunk.metadata.update(
                    {
                        "project_id": document.project_id,
                        "material_id": document.material_id,
                        "document_id": document.document_id,
                    }
                )
            ids = [f"{document.document_id}:{chunk.metadata['chunk_index']}" for chunk in chunks]
            self.vector_index.add_documents(chunks, ids)
            self.store.mark_document_indexed(document.document_id, content, len(chunks))
        except EmptyDocument as exc:
            self.store.mark_document_failed(document.document_id, str(exc), content)
            _invalid_document(str(exc))
        except Exception as exc:
            self.store.mark_document_failed(document.document_id, str(exc), content)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"code": "INDEXING_FAILED", "message": "Document indexing failed."},
            ) from exc
        return self.document_status(document.document_id)

    def document_status(self, document_id: str) -> DocumentStatusResponse:
        document = self.store.get_document(document_id)
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "DOCUMENT_NOT_FOUND", "message": "Document not found."},
            )
        return document

    def document_content(self, document_id: str) -> DocumentContentResponse:
        document = self.document_status(document_id)
        content = self.store.get_document_content(document_id)
        if content is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "DOCUMENT_CONTENT_NOT_FOUND",
                    "message": "Document content not found.",
                },
            )
        return DocumentContentResponse(**document.model_dump(), content=content)

    async def search(self, request: SearchRequest) -> SearchResponse:
        matches = self.vector_index.search(request.query, request.project_id, request.top_k)
        chunks = [
            SearchChunk(
                document_id=str(document.metadata["document_id"]),
                project_id=str(document.metadata["project_id"]),
                material_id=str(document.metadata["material_id"]),
                file_name=str(document.metadata["file_name"]),
                location=_source_location(document.metadata),
                chunk_index=int(document.metadata["chunk_index"]),
                chunk_text=document.page_content,
                score=float(score),
            )
            for document, score in matches
        ]
        return SearchResponse(chunks=chunks)

    async def chat(self, request: ChatRequest) -> ChatResponse:
        started = time.perf_counter()
        search = await self.search(
            SearchRequest(project_id=request.project_id, query=request.message, top_k=request.top_k)
        )
        if not search.chunks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "NO_INDEXED_DOCUMENTS",
                    "message": "Envie um documento em Materiais antes de fazer perguntas.",
                },
            )
        history = self.store.get_history(request.session_id)[
            -(self.settings.max_history_turns * 2) :
        ]
        try:
            answer, model = await self.chat_client.complete(  # type: ignore[attr-defined]
                request.message, search.chunks, history, self.settings.max_context_words
            )
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"code": "LLM_UNAVAILABLE", "message": str(exc)},
            ) from exc
        self.store.append_turns(request.project_id, request.session_id, request.message, answer)
        return ChatResponse(
            session_id=request.session_id,
            answer=answer,
            model_used=model,
            sources=source_items(search.chunks),
            latency_ms=int((time.perf_counter() - started) * 1000),
        )

    def history(self, session_id: str) -> HistoryResponse:
        return HistoryResponse(session_id=session_id, turns=self.store.get_history(session_id))

    def delete_history(self, session_id: str) -> None:
        self.store.delete_history(session_id)

    def feedback(self, request: FeedbackRequest) -> FeedbackResponse:
        self.store.submit_feedback(request)
        return FeedbackResponse(accepted=True, message_id=request.message_id)


def source_items(chunks: list[SearchChunk]) -> list[SourceItem]:
    sources: list[SourceItem] = []
    document_ids: set[str] = set()
    for chunk in chunks:
        if chunk.document_id in document_ids:
            continue
        document_ids.add(chunk.document_id)
        sources.append(
            SourceItem(
                document_id=chunk.document_id,
                material_id=chunk.material_id,
                file_name=chunk.file_name,
                location=chunk.location,
                chunk_index=chunk.chunk_index,
                score=chunk.score,
            )
        )
    return sources


def _source_location(metadata: dict) -> str:
    file_name = str(metadata["file_name"])
    page = metadata.get("page")
    if isinstance(page, int):
        return f"{file_name} (pagina {page + 1})"
    header = metadata.get("header_2") or metadata.get("header_1")
    return f"{file_name} ({header})" if header else file_name


def _invalid_document(message: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail={"code": "INVALID_DOCUMENT", "message": message},
    )


def _project_not_found() -> None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"code": "PROJECT_NOT_FOUND", "message": "Project not found."},
    )
