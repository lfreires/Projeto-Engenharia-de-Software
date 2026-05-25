import hashlib
import json
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
    TokenValidationResponse,
    UserItem,
)

DOCUMENT_FIELDS = (
    "id AS document_id, project_id, material_id, file_name, content_type, "
    "status, chunk_count, error_message"
)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def content_digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def new_document_id() -> str:
    return f"doc-{uuid.uuid4().hex}"


def new_material_id() -> str:
    return f"mat-{uuid.uuid4().hex}"


def new_version_id() -> str:
    return f"ver-{uuid.uuid4().hex}"


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

    def list_material_documents(
        self, project_id: str, material_id: str
    ) -> list[DocumentStatusResponse]: ...

    def delete_material(self, project_id: str, material_id: str) -> bool: ...

    def get_document_by_hash(
        self, project_id: str, material_id: str, content_hash: str
    ) -> DocumentStatusResponse | None: ...

    def create_upload_document(
        self,
        project_id: str,
        title: str,
        file_name: str,
        content_type: str,
        content_hash: str,
    ) -> DocumentStatusResponse: ...

    def create_document_version(
        self,
        project_id: str,
        material_id: str,
        file_name: str,
        content_type: str,
        content_hash: str,
    ) -> DocumentStatusResponse: ...

    def mark_document_indexed(self, document_id: str, content: str, chunk_count: int) -> None: ...

    def mark_document_failed(
        self, document_id: str, error_message: str, content: str | None = None
    ) -> None: ...

    def get_document(self, document_id: str) -> DocumentStatusResponse | None: ...

    def get_document_content(self, document_id: str) -> str | None: ...

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

    def validate_token(self, token: str, project_id: str | None) -> TokenValidationResponse | None:
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
                "JOIN documents d ON d.id = v.document_id AND d.status = 'indexed' "
                "WHERE m.project_id = %s ORDER BY m.created_at DESC",
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

    def list_material_documents(
        self, project_id: str, material_id: str
    ) -> list[DocumentStatusResponse]:
        with self._connection() as connection:
            rows = connection.execute(
                f"SELECT {DOCUMENT_FIELDS} FROM documents "
                "WHERE project_id = %s AND material_id = %s ORDER BY id",
                (project_id, material_id),
            ).fetchall()
        return [DocumentStatusResponse(**row) for row in rows]

    def delete_material(self, project_id: str, material_id: str) -> bool:
        with self._connection() as connection:
            row = connection.execute(
                "DELETE FROM materials WHERE project_id = %s AND id = %s RETURNING id",
                (project_id, material_id),
            ).fetchone()
            connection.commit()
        return row is not None

    def get_document_by_hash(
        self, project_id: str, material_id: str, content_hash: str
    ) -> DocumentStatusResponse | None:
        with self._connection() as connection:
            row = connection.execute(
                f"SELECT {DOCUMENT_FIELDS} FROM documents "
                "WHERE project_id = %s AND material_id = %s AND content_hash = %s",
                (project_id, material_id, content_hash),
            ).fetchone()
        return DocumentStatusResponse(**row) if row else None

    def create_upload_document(
        self,
        project_id: str,
        title: str,
        file_name: str,
        content_type: str,
        content_hash: str,
    ) -> DocumentStatusResponse:
        material_id = new_material_id()
        document = _pending_document(project_id, material_id, file_name, content_type)
        with self._connection() as connection:
            connection.execute(
                "INSERT INTO materials (id, project_id, title, content_type) "
                "VALUES (%s, %s, %s, %s)",
                (material_id, project_id, title, content_type),
            )
            self._insert_document(connection, document, content_hash, 1)
            connection.commit()
        return document

    def create_document_version(
        self,
        project_id: str,
        material_id: str,
        file_name: str,
        content_type: str,
        content_hash: str,
    ) -> DocumentStatusResponse:
        document = _pending_document(project_id, material_id, file_name, content_type)
        with self._connection() as connection:
            version = connection.execute(
                "SELECT COALESCE(max(version), 0) + 1 AS version FROM material_versions "
                "WHERE material_id = %s",
                (material_id,),
            ).fetchone()["version"]
            self._insert_document(connection, document, content_hash, version)
            connection.commit()
        return document

    def _insert_document(
        self, connection: Any, document: DocumentStatusResponse, content_hash: str, version: int
    ) -> None:
        connection.execute(
            "INSERT INTO documents "
            "(id, project_id, material_id, file_name, content_type, content_hash, "
            "status, chunk_count) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (
                document.document_id,
                document.project_id,
                document.material_id,
                document.file_name,
                document.content_type,
                content_hash,
                document.status,
                document.chunk_count,
            ),
        )
        connection.execute(
            "INSERT INTO material_versions "
            "(id, material_id, version, document_id, file_name) VALUES (%s, %s, %s, %s, %s)",
            (
                new_version_id(),
                document.material_id,
                version,
                document.document_id,
                document.file_name,
            ),
        )

    def mark_document_indexed(self, document_id: str, content: str, chunk_count: int) -> None:
        with self._connection() as connection:
            connection.execute(
                "UPDATE documents SET content = %s, status = 'indexed', chunk_count = %s, "
                "error_message = NULL WHERE id = %s",
                (content, chunk_count, document_id),
            )
            connection.commit()

    def mark_document_failed(
        self, document_id: str, error_message: str, content: str | None = None
    ) -> None:
        with self._connection() as connection:
            connection.execute(
                "UPDATE documents SET content = COALESCE(%s, content), status = 'failed', "
                "error_message = %s WHERE id = %s",
                (content, error_message[:1000], document_id),
            )
            connection.commit()

    def get_document(self, document_id: str) -> DocumentStatusResponse | None:
        with self._connection() as connection:
            row = connection.execute(
                f"SELECT {DOCUMENT_FIELDS} FROM documents WHERE id = %s", (document_id,)
            ).fetchone()
        return DocumentStatusResponse(**row) if row else None

    def get_document_content(self, document_id: str) -> str | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT content FROM documents WHERE id = %s", (document_id,)
            ).fetchone()
        return row["content"] if row and row["content"] is not None else None

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
                    "VALUES (%s, %s, %s, true, %s::jsonb) ON CONFLICT (token_hash) DO NOTHING",
                    (token_hash(token), subject_id, subject_type, json.dumps(token_permissions)),
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
        self.document_contents: dict[str, str] = {}
        self.document_hashes: dict[tuple[str, str, str], str] = {}
        self.history: dict[str, list[HistoryTurn]] = {}
        self.feedback: dict[str, FeedbackRequest] = {}

    def validate_token(self, token: str, project_id: str | None) -> TokenValidationResponse | None:
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
            material
            for material in self.materials.values()
            if material.project_id == project_id
            and self.documents.get(material.latest_version.document_id) is not None
            and self.documents[material.latest_version.document_id].status == "indexed"
        ]

    def has_material(self, project_id: str, material_id: str) -> bool:
        material = self.materials.get(material_id)
        return material is not None and material.project_id == project_id

    def list_material_documents(
        self, project_id: str, material_id: str
    ) -> list[DocumentStatusResponse]:
        return [
            document
            for document in self.documents.values()
            if document.project_id == project_id and document.material_id == material_id
        ]

    def delete_material(self, project_id: str, material_id: str) -> bool:
        if not self.has_material(project_id, material_id):
            return False
        document_ids = {
            document.document_id
            for document in self.list_material_documents(project_id, material_id)
        }
        self.materials.pop(material_id, None)
        for document_id in document_ids:
            self.documents.pop(document_id, None)
            self.document_contents.pop(document_id, None)
        self.document_hashes = {
            key: document_id
            for key, document_id in self.document_hashes.items()
            if document_id not in document_ids
        }
        return True

    def get_document_by_hash(
        self, project_id: str, material_id: str, content_hash: str
    ) -> DocumentStatusResponse | None:
        document_id = self.document_hashes.get((project_id, material_id, content_hash))
        return self.documents.get(document_id) if document_id else None

    def create_upload_document(
        self,
        project_id: str,
        title: str,
        file_name: str,
        content_type: str,
        content_hash: str,
    ) -> DocumentStatusResponse:
        material_id = new_material_id()
        document = _pending_document(project_id, material_id, file_name, content_type)
        self.materials[material_id] = Material(
            id=material_id,
            project_id=project_id,
            title=title,
            content_type=content_type,
            latest_version=_version(material_id, 1, document),
        )
        self._store_pending(document, content_hash)
        return document

    def create_document_version(
        self,
        project_id: str,
        material_id: str,
        file_name: str,
        content_type: str,
        content_hash: str,
    ) -> DocumentStatusResponse:
        document = _pending_document(project_id, material_id, file_name, content_type)
        material = self.materials[material_id]
        material.latest_version = _version(
            material_id, material.latest_version.version + 1, document
        )
        self._store_pending(document, content_hash)
        return document

    def _store_pending(self, document: DocumentStatusResponse, content_hash: str) -> None:
        self.documents[document.document_id] = document
        self.document_hashes[(document.project_id, document.material_id, content_hash)] = (
            document.document_id
        )

    def mark_document_indexed(self, document_id: str, content: str, chunk_count: int) -> None:
        self.documents[document_id] = self.documents[document_id].model_copy(
            update={"status": "indexed", "chunk_count": chunk_count, "error_message": None}
        )
        self.document_contents[document_id] = content

    def mark_document_failed(
        self, document_id: str, error_message: str, content: str | None = None
    ) -> None:
        self.documents[document_id] = self.documents[document_id].model_copy(
            update={"status": "failed", "error_message": error_message[:1000]}
        )
        if content is not None:
            self.document_contents[document_id] = content

    def get_document(self, document_id: str) -> DocumentStatusResponse | None:
        return self.documents.get(document_id)

    def get_document_content(self, document_id: str) -> str | None:
        return self.document_contents.get(document_id)

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
                project_id="proj-demo", user_id="user-demo", role="owner", permissions=permissions
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


def _pending_document(
    project_id: str, material_id: str, file_name: str, content_type: str
) -> DocumentStatusResponse:
    return DocumentStatusResponse(
        document_id=new_document_id(),
        project_id=project_id,
        material_id=material_id,
        file_name=file_name,
        content_type=content_type,
        status="processing",
        chunk_count=0,
    )


def _version(material_id: str, number: int, document: DocumentStatusResponse) -> MaterialVersion:
    return MaterialVersion(
        id=new_version_id(),
        material_id=material_id,
        version=number,
        document_id=document.document_id,
        file_name=document.file_name,
        created_at=datetime.now(UTC),
    )
