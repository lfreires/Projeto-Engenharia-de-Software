import hashlib
import json
import math
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

from app.config import Settings
from app.schemas import (
    DocumentStatusResponse,
    FeedbackRequest,
    HistoryTurn,
    Material,
    MaterialVersion,
    MembershipItem,
    Project,
    SearchChunk,
    TokenValidationResponse,
    UserItem,
)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class Store(Protocol):
    def validate_token(
        self, token: str, project_id: str | None
    ) -> TokenValidationResponse | None: ...

    def list_users(self) -> list[UserItem]: ...

    def list_memberships(self, project_id: str | None = None) -> list[MembershipItem]: ...

    def list_projects(self) -> list[Project]: ...

    def get_project(self, project_id: str) -> Project | None: ...

    def list_materials(self, project_id: str) -> list[Material]: ...

    def has_material(self, project_id: str, material_id: str) -> bool: ...

    def get_document_by_hash(
        self, project_id: str, material_id: str, content_hash: str
    ) -> DocumentStatusResponse | None: ...

    def add_document(
        self,
        document: DocumentStatusResponse,
        content_hash: str,
        chunks: list[tuple[str, list[float]]],
        embedding_model: str,
        embedding_dimensions: int,
    ) -> None: ...

    def get_document(self, document_id: str) -> DocumentStatusResponse | None: ...

    def search(
        self,
        project_id: str,
        embedding: list[float],
        top_k: int,
        embedding_model: str,
        embedding_dimensions: int,
    ) -> list[SearchChunk]: ...

    def get_history(self, session_id: str) -> list[HistoryTurn]: ...

    def append_turns(
        self, project_id: str, session_id: str, user_message: str, assistant_answer: str
    ) -> None: ...

    def delete_history(self, session_id: str) -> None: ...

    def submit_feedback(self, request: FeedbackRequest) -> None: ...

    def seed_catalog_and_identity(self, bearer_token: str, internal_token: str) -> None: ...


class PostgresStore:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @contextmanager
    def _connection(self) -> Iterator[Any]:
        import psycopg
        from psycopg.rows import dict_row

        with psycopg.connect(
            self._settings.database_url,
            row_factory=dict_row,
            prepare_threshold=None,
        ) as connection:
            yield connection

    def apply_migrations(self, migration_directory: Path) -> None:
        with self._connection() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS schema_migrations "
                "(version TEXT PRIMARY KEY, applied_at TIMESTAMPTZ NOT NULL DEFAULT now())"
            )
            for path in sorted(migration_directory.glob("*.sql")):
                existing = connection.execute(
                    "SELECT 1 FROM schema_migrations WHERE version = %s", (path.name,)
                ).fetchone()
                if existing:
                    continue
                connection.execute(path.read_text(encoding="utf-8"))
                connection.execute(
                    "INSERT INTO schema_migrations (version) VALUES (%s)", (path.name,)
                )
            connection.commit()

    def validate_token(
        self, token: str, project_id: str | None
    ) -> TokenValidationResponse | None:
        with self._connection() as connection:
            record = connection.execute(
                "SELECT subject_id, subject_type, permissions FROM api_tokens "
                "WHERE token_hash = %s AND active = true",
                (token_hash(token),),
            ).fetchone()
            if record is None:
                return None
            if project_id and record["subject_type"] == "user":
                membership = connection.execute(
                    "SELECT permissions FROM project_memberships "
                    "WHERE project_id = %s AND user_id = %s",
                    (project_id, record["subject_id"]),
                ).fetchone()
                if membership is None:
                    return None
                permissions = membership["permissions"]
            else:
                permissions = record["permissions"]
        return TokenValidationResponse(
            active=True,
            subject_id=record["subject_id"],
            subject_type=record["subject_type"],
            project_id=project_id,
            permissions=permissions,
        )

    def list_users(self) -> list[UserItem]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT id, email, display_name FROM users ORDER BY id"
            ).fetchall()
        return [UserItem(**row) for row in rows]

    def list_memberships(self, project_id: str | None = None) -> list[MembershipItem]:
        query = "SELECT project_id, user_id, role, permissions FROM project_memberships"
        params: tuple[str, ...] = ()
        if project_id:
            query += " WHERE project_id = %s"
            params = (project_id,)
        query += " ORDER BY project_id, user_id"
        with self._connection() as connection:
            rows = connection.execute(query, params).fetchall()
        return [MembershipItem(**row) for row in rows]

    def list_projects(self) -> list[Project]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT id, name, description, created_at FROM projects ORDER BY created_at"
            ).fetchall()
        return [Project(**row) for row in rows]

    def get_project(self, project_id: str) -> Project | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT id, name, description, created_at FROM projects WHERE id = %s",
                (project_id,),
            ).fetchone()
        return Project(**row) if row else None

    def list_materials(self, project_id: str) -> list[Material]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT m.id, m.project_id, m.title, m.content_type, v.id AS version_id, "
                "v.version, v.document_id, v.file_name, v.created_at "
                "FROM materials m JOIN LATERAL "
                "(SELECT id, material_id, version, document_id, file_name, created_at "
                "FROM material_versions WHERE material_id = m.id "
                "ORDER BY version DESC LIMIT 1) v ON true "
                "WHERE m.project_id = %s ORDER BY m.id",
                (project_id,),
            ).fetchall()
        return [
            Material(
                id=row["id"],
                project_id=row["project_id"],
                title=row["title"],
                content_type=row["content_type"],
                latest_version=MaterialVersion(
                    id=row["version_id"],
                    material_id=row["id"],
                    version=row["version"],
                    document_id=row["document_id"],
                    file_name=row["file_name"],
                    created_at=row["created_at"],
                ),
            )
            for row in rows
        ]

    def has_material(self, project_id: str, material_id: str) -> bool:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT 1 FROM materials WHERE project_id = %s AND id = %s",
                (project_id, material_id),
            ).fetchone()
        return row is not None

    def get_document_by_hash(
        self, project_id: str, material_id: str, content_hash: str
    ) -> DocumentStatusResponse | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT id AS document_id, project_id, material_id, file_name, status, chunk_count "
                "FROM documents WHERE project_id = %s AND material_id = %s AND content_hash = %s",
                (project_id, material_id, content_hash),
            ).fetchone()
        return DocumentStatusResponse(**row) if row else None

    def add_document(
        self,
        document: DocumentStatusResponse,
        content_hash: str,
        chunks: list[tuple[str, list[float]]],
        embedding_model: str,
        embedding_dimensions: int,
    ) -> None:
        with self._connection() as connection:
            connection.execute(
                "INSERT INTO documents "
                "(id, project_id, material_id, file_name, content_hash, status, chunk_count) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    document.document_id,
                    document.project_id,
                    document.material_id,
                    document.file_name,
                    content_hash,
                    document.status,
                    document.chunk_count,
                ),
            )
            for index, (text, embedding) in enumerate(chunks):
                connection.execute(
                    "INSERT INTO document_chunks "
                    "(document_id, project_id, material_id, file_name, chunk_index, chunk_text, "
                    "embedding_model, embedding_dimensions, embedding) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::extensions.vector)",
                    (
                        document.document_id,
                        document.project_id,
                        document.material_id,
                        document.file_name,
                        index,
                        text,
                        embedding_model,
                        embedding_dimensions,
                        _vector_literal(embedding),
                    ),
                )
            connection.execute(
                "UPDATE material_versions SET document_id = %s, file_name = %s "
                "WHERE material_id = %s AND version = "
                "(SELECT max(version) FROM material_versions WHERE material_id = %s)",
                (
                    document.document_id,
                    document.file_name,
                    document.material_id,
                    document.material_id,
                ),
            )
            connection.commit()

    def get_document(self, document_id: str) -> DocumentStatusResponse | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT id AS document_id, project_id, material_id, file_name, status, chunk_count "
                "FROM documents WHERE id = %s",
                (document_id,),
            ).fetchone()
        return DocumentStatusResponse(**row) if row else None

    def search(
        self,
        project_id: str,
        embedding: list[float],
        top_k: int,
        embedding_model: str,
        embedding_dimensions: int,
    ) -> list[SearchChunk]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT document_id, project_id, material_id, file_name, chunk_index, chunk_text, "
                "file_name || '#chunk-' || chunk_index AS location, "
                "1 - (embedding OPERATOR(extensions.<=>) %s::extensions.vector) AS score "
                "FROM document_chunks WHERE project_id = %s AND embedding_model = %s "
                "AND embedding_dimensions = %s "
                "ORDER BY embedding OPERATOR(extensions.<=>) %s::extensions.vector LIMIT %s",
                (
                    _vector_literal(embedding),
                    project_id,
                    embedding_model,
                    embedding_dimensions,
                    _vector_literal(embedding),
                    top_k,
                ),
            ).fetchall()
        return [SearchChunk(**row) for row in rows]

    def get_history(self, session_id: str) -> list[HistoryTurn]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT role, content, created_at AS timestamp FROM messages "
                "WHERE session_id = %s ORDER BY created_at, id",
                (session_id,),
            ).fetchall()
        return [HistoryTurn(**row) for row in rows]

    def append_turns(
        self, project_id: str, session_id: str, user_message: str, assistant_answer: str
    ) -> None:
        with self._connection() as connection:
            connection.execute(
                "INSERT INTO chat_sessions (id, project_id) VALUES (%s, %s) "
                "ON CONFLICT (id) DO NOTHING",
                (session_id, project_id),
            )
            with connection.cursor() as cursor:
                cursor.executemany(
                    "INSERT INTO messages (session_id, role, content) VALUES (%s, %s, %s)",
                    [
                        (session_id, "user", user_message),
                        (session_id, "assistant", assistant_answer),
                    ],
                )
            connection.commit()

    def delete_history(self, session_id: str) -> None:
        with self._connection() as connection:
            connection.execute("DELETE FROM chat_sessions WHERE id = %s", (session_id,))
            connection.commit()

    def submit_feedback(self, request: FeedbackRequest) -> None:
        with self._connection() as connection:
            connection.execute(
                "INSERT INTO feedback (message_id, session_id, rating, comment) "
                "VALUES (%s, %s, %s, %s) "
                "ON CONFLICT (message_id) DO UPDATE SET rating = EXCLUDED.rating, "
                "comment = EXCLUDED.comment, updated_at = now()",
                (request.message_id, request.session_id, request.rating, request.comment),
            )
            connection.commit()

    def seed_catalog_and_identity(self, bearer_token: str, internal_token: str) -> None:
        permissions = ["project:read", "material:read", "query:chat"]
        with self._connection() as connection:
            connection.execute(
                "INSERT INTO users (id, email, display_name) VALUES (%s, %s, %s) "
                "ON CONFLICT (id) DO NOTHING",
                ("user-demo", "demo@docai.local", "Demo User"),
            )
            connection.execute(
                "INSERT INTO projects (id, name, description) VALUES (%s, %s, %s) "
                "ON CONFLICT (id) DO NOTHING",
                ("proj-demo", "DocAI Demo", "Projeto demonstrativo publicado no Render."),
            )
            connection.execute(
                "INSERT INTO project_memberships (project_id, user_id, role, permissions) "
                "VALUES (%s, %s, %s, %s::jsonb) ON CONFLICT (project_id, user_id) DO NOTHING",
                ("proj-demo", "user-demo", "owner", json.dumps(permissions)),
            )
            for token, subject_id, subject_type, token_permissions in [
                (bearer_token, "user-demo", "user", permissions),
                (
                    internal_token,
                    "query-service",
                    "service",
                    ["ingestion:search", "identity:validate"],
                ),
            ]:
                connection.execute(
                    "INSERT INTO api_tokens "
                    "(token_hash, subject_id, subject_type, active, permissions) "
                    "VALUES (%s, %s, %s, true, %s::jsonb) "
                    "ON CONFLICT (token_hash) DO NOTHING",
                    (token_hash(token), subject_id, subject_type, json.dumps(token_permissions)),
                )
            connection.execute(
                "INSERT INTO materials (id, project_id, title, content_type) "
                "VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
                ("mat-architecture", "proj-demo", "Arquitetura DocAI", "text/markdown"),
            )
            connection.execute(
                "INSERT INTO material_versions "
                "(id, material_id, version, document_id, file_name) VALUES (%s, %s, %s, %s, %s) "
                "ON CONFLICT (id) DO NOTHING",
                (
                    "mat-architecture-v1",
                    "mat-architecture",
                    1,
                    "pending-seed-document",
                    "architecture.md",
                ),
            )
            connection.commit()


class MemoryStore:
    """Development store; production configuration always selects PostgresStore."""

    def __init__(self) -> None:
        self.users: dict[str, UserItem] = {}
        self.tokens: dict[str, dict[str, Any]] = {}
        self.memberships: dict[tuple[str, str], MembershipItem] = {}
        self.projects: dict[str, Project] = {}
        self.materials: dict[str, Material] = {}
        self.documents: dict[str, DocumentStatusResponse] = {}
        self.document_hashes: dict[tuple[str, str, str], str] = {}
        self.chunks: list[tuple[SearchChunk, list[float], str, int]] = []
        self.history: dict[str, list[HistoryTurn]] = {}
        self.feedback: dict[str, FeedbackRequest] = {}

    def validate_token(
        self, token: str, project_id: str | None
    ) -> TokenValidationResponse | None:
        record = self.tokens.get(token_hash(token))
        if record is None:
            return None
        permissions = record["permissions"]
        if project_id and record["subject_type"] == "user":
            membership = self.memberships.get((project_id, record["subject_id"]))
            if membership is None:
                return None
            permissions = membership.permissions
        return TokenValidationResponse(
            active=True,
            subject_id=record["subject_id"],
            subject_type=record["subject_type"],
            project_id=project_id,
            permissions=permissions,
        )

    def list_users(self) -> list[UserItem]:
        return list(self.users.values())

    def list_memberships(self, project_id: str | None = None) -> list[MembershipItem]:
        result = list(self.memberships.values())
        if project_id:
            result = [membership for membership in result if membership.project_id == project_id]
        return result

    def list_projects(self) -> list[Project]:
        return list(self.projects.values())

    def get_project(self, project_id: str) -> Project | None:
        return self.projects.get(project_id)

    def list_materials(self, project_id: str) -> list[Material]:
        return [
            material for material in self.materials.values() if material.project_id == project_id
        ]

    def has_material(self, project_id: str, material_id: str) -> bool:
        material = self.materials.get(material_id)
        return material is not None and material.project_id == project_id

    def get_document_by_hash(
        self, project_id: str, material_id: str, content_hash: str
    ) -> DocumentStatusResponse | None:
        document_id = self.document_hashes.get((project_id, material_id, content_hash))
        return self.documents.get(document_id) if document_id else None

    def add_document(
        self,
        document: DocumentStatusResponse,
        content_hash: str,
        chunks: list[tuple[str, list[float]]],
        embedding_model: str,
        embedding_dimensions: int,
    ) -> None:
        self.documents[document.document_id] = document
        self.document_hashes[(document.project_id, document.material_id, content_hash)] = (
            document.document_id
        )
        for index, (text, embedding) in enumerate(chunks):
            self.chunks.append(
                (
                    SearchChunk(
                        document_id=document.document_id,
                        project_id=document.project_id,
                        material_id=document.material_id,
                        file_name=document.file_name,
                        location=f"{document.file_name}#chunk-{index}",
                        chunk_index=index,
                        chunk_text=text,
                        score=0,
                    ),
                    embedding,
                    embedding_model,
                    embedding_dimensions,
                )
            )
        material = self.materials.get(document.material_id)
        if material:
            material.latest_version.document_id = document.document_id
            material.latest_version.file_name = document.file_name

    def get_document(self, document_id: str) -> DocumentStatusResponse | None:
        return self.documents.get(document_id)

    def search(
        self,
        project_id: str,
        embedding: list[float],
        top_k: int,
        embedding_model: str,
        embedding_dimensions: int,
    ) -> list[SearchChunk]:
        results: list[SearchChunk] = []
        for chunk, stored_embedding, model, dimensions in self.chunks:
            if (
                chunk.project_id != project_id
                or model != embedding_model
                or dimensions != embedding_dimensions
            ):
                continue
            score = _cosine_similarity(embedding, stored_embedding)
            if score > 0:
                results.append(chunk.model_copy(update={"score": score}))
        results.sort(key=lambda result: result.score, reverse=True)
        return results[:top_k]

    def get_history(self, session_id: str) -> list[HistoryTurn]:
        return list(self.history.get(session_id, []))

    def append_turns(
        self, project_id: str, session_id: str, user_message: str, assistant_answer: str
    ) -> None:
        del project_id
        turns = self.history.setdefault(session_id, [])
        turns.extend(
            [
                HistoryTurn(role="user", content=user_message),
                HistoryTurn(role="assistant", content=assistant_answer),
            ]
        )

    def delete_history(self, session_id: str) -> None:
        self.history.pop(session_id, None)

    def submit_feedback(self, request: FeedbackRequest) -> None:
        self.feedback[request.message_id] = request

    def seed_catalog_and_identity(self, bearer_token: str, internal_token: str) -> None:
        permissions = ["project:read", "material:read", "query:chat"]
        self.users.setdefault(
            "user-demo",
            UserItem(id="user-demo", email="demo@docai.local", display_name="Demo User"),
        )
        self.projects.setdefault(
            "proj-demo",
            Project(
                id="proj-demo",
                name="DocAI Demo",
                description="Projeto demonstrativo publicado no Render.",
                created_at=datetime(2026, 1, 1, tzinfo=UTC),
            ),
        )
        self.memberships.setdefault(
            ("proj-demo", "user-demo"),
            MembershipItem(
                project_id="proj-demo",
                user_id="user-demo",
                role="owner",
                permissions=permissions,
            ),
        )
        self.tokens.setdefault(
            token_hash(bearer_token),
            {"subject_id": "user-demo", "subject_type": "user", "permissions": permissions},
        )
        self.tokens.setdefault(
            token_hash(internal_token),
            {
                "subject_id": "query-service",
                "subject_type": "service",
                "permissions": ["ingestion:search", "identity:validate"],
            },
        )
        self.materials.setdefault(
            "mat-architecture",
            Material(
                id="mat-architecture",
                project_id="proj-demo",
                title="Arquitetura DocAI",
                content_type="text/markdown",
                latest_version=MaterialVersion(
                    id="mat-architecture-v1",
                    material_id="mat-architecture",
                    version=1,
                    document_id="pending-seed-document",
                    file_name="architecture.md",
                    created_at=datetime(2026, 1, 1, tzinfo=UTC),
                ),
            ),
        )


def new_document_id() -> str:
    return f"doc-{uuid.uuid4().hex}"


def content_digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _vector_literal(values: list[float]) -> str:
    return "[" + ",".join(str(float(value)) for value in values) + "]"


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if not left_norm or not right_norm:
        return 0.0
    return numerator / (left_norm * right_norm)
