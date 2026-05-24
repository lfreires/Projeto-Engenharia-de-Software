import time
from dataclasses import dataclass

from fastapi import HTTPException, status

from app.config import Settings
from app.schemas import (
    ChatRequest,
    ChatResponse,
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
from app.storage import Store, content_digest, new_document_id

SEED_DOCUMENT = """# DocAI no Render

O DocAI e uma aplicacao RAG publicada como monorepo. O Render executa uma API
FastAPI unica que tambem entrega o frontend React. Os dados persistentes e os
vetores ficam no PostgreSQL do Supabase com pgvector. O Gemini gera embeddings
e o Groq gera respostas fundamentadas nos documentos recuperados.
"""


@dataclass
class Services:
    settings: Settings
    store: Store
    embedding_client: object
    chat_client: object

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
        await self.index_document(
            DocumentCreateRequest(
                project_id="proj-demo",
                material_id="mat-architecture",
                file_name="architecture.md",
                content=SEED_DOCUMENT,
            )
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

    async def index_document(self, request: DocumentCreateRequest) -> DocumentStatusResponse:
        if self.store.get_project(request.project_id) is None:
            _project_not_found()
        if not self.store.has_material(request.project_id, request.material_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "MATERIAL_NOT_FOUND", "message": "Material not found."},
            )
        digest = content_digest(request.content)
        existing = self.store.get_document_by_hash(
            request.project_id, request.material_id, digest
        )
        if existing:
            return existing
        texts = chunk_text(request.content, self.settings.default_chunk_max_words)
        chunks = [
            (text, await self.embedding_client.embed_document(text))  # type: ignore[attr-defined]
            for text in texts
        ]
        document = DocumentStatusResponse(
            document_id=new_document_id(),
            project_id=request.project_id,
            material_id=request.material_id,
            file_name=request.file_name,
            status="indexed",
            chunk_count=len(chunks),
        )
        self.store.add_document(
            document,
            digest,
            chunks,
            self.settings.embedding_model,
            self.settings.embedding_dimensions,
        )
        return document

    def document_status(self, document_id: str) -> DocumentStatusResponse:
        document = self.store.get_document(document_id)
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "DOCUMENT_NOT_FOUND", "message": "Document not found."},
            )
        return document

    async def search(self, request: SearchRequest) -> SearchResponse:
        vector = await self.embedding_client.embed_query(request.query)  # type: ignore[attr-defined]
        chunks = self.store.search(
            request.project_id,
            vector,
            request.top_k,
            self.settings.embedding_model,
            self.settings.embedding_dimensions,
        )
        return SearchResponse(chunks=chunks)

    async def chat(self, request: ChatRequest) -> ChatResponse:
        started = time.perf_counter()
        search = await self.search(
            SearchRequest(
                project_id=request.project_id,
                query=request.message,
                top_k=request.top_k,
            )
        )
        if not search.chunks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "PROJECT_NOT_FOUND",
                    "message": f"No documents indexed for project '{request.project_id}'",
                },
            )
        history = self.store.get_history(request.session_id)[
            -(self.settings.max_history_turns * 2) :
        ]
        messages = build_messages(
            request.message,
            search.chunks,
            history,
            self.settings.max_context_words,
        )
        try:
            answer, model = await self.chat_client.complete(messages)  # type: ignore[attr-defined]
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"code": "LLM_UNAVAILABLE", "message": str(exc)},
            )
        self.store.append_turns(request.project_id, request.session_id, request.message, answer)
        return ChatResponse(
            session_id=request.session_id,
            answer=answer,
            model_used=model,
            sources=[
                SourceItem(
                    document_id=chunk.document_id,
                    material_id=chunk.material_id,
                    file_name=chunk.file_name,
                    location=chunk.location,
                    chunk_index=chunk.chunk_index,
                    score=chunk.score,
                )
                for chunk in search.chunks
            ],
            latency_ms=int((time.perf_counter() - started) * 1000),
        )

    def history(self, session_id: str) -> HistoryResponse:
        return HistoryResponse(session_id=session_id, turns=self.store.get_history(session_id))

    def delete_history(self, session_id: str) -> None:
        self.store.delete_history(session_id)

    def feedback(self, request: FeedbackRequest) -> FeedbackResponse:
        self.store.submit_feedback(request)
        return FeedbackResponse(accepted=True, message_id=request.message_id)


def chunk_text(content: str, max_words: int) -> list[str]:
    words = content.split()
    return [" ".join(words[start : start + max_words]) for start in range(0, len(words), max_words)]


def build_messages(
    question: str,
    chunks: list[SearchChunk],
    history: list,
    max_context_words: int,
) -> list[dict[str, str]]:
    context = "\n\n".join(
        f"[{chunk.file_name}#chunk-{chunk.chunk_index}] {chunk.chunk_text}" for chunk in chunks
    )
    context = " ".join(context.split()[:max_context_words])
    messages = [
        {
            "role": "system",
            "content": (
                "Responda somente com base no contexto recuperado. "
                "Quando apropriado, cite o arquivo e o chunk usados."
            ),
        }
    ]
    messages.extend({"role": turn.role, "content": turn.content} for turn in history)
    messages.append(
        {"role": "user", "content": f"Contexto:\n{context}\n\nPergunta: {question}"}
    )
    return messages


def _project_not_found() -> None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"code": "PROJECT_NOT_FOUND", "message": "Project not found."},
    )
