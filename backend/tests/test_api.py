from datetime import UTC, datetime
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from langchain_core.documents import Document

import app.rag as rag
from app.config import Settings
from app.main import build_services, create_app
from app.rag import DeterministicEmbeddings, MemoryVectorIndex
from app.schemas import Project
from app.services import Services
from app.storage import MemoryStore

AUTH = {"Authorization": "Bearer dev-token"}
INTERNAL_AUTH = {"Authorization": "Bearer internal-query-token"}


class FakeChatClient:
    async def complete(self, question, chunks, history, max_context_words):
        del history, max_context_words
        assert question
        assert chunks
        assert "#chunk-" not in chunks[0].location
        return f"Resposta baseada em [{chunks[0].file_name}].", "fake-groq-model"


class FailingAppendStore(MemoryStore):
    def append_turns(
        self, project_id: str, session_id: str, user_message: str, assistant_answer: str
    ) -> None:
        raise RuntimeError("database write failed")


class FailingVectorIndex(MemoryVectorIndex):
    def add_documents(self, documents, ids):
        del documents, ids
        raise RuntimeError("embedding unavailable")


class FailingDeleteVectorIndex(MemoryVectorIndex):
    def delete_documents(self, documents):
        del documents
        raise RuntimeError("vector delete unavailable")


def make_services(store: MemoryStore | None = None, vector_index=None) -> Services:
    settings = Settings(seed_demo_data=False, embedding_dimensions=768)
    services = Services(
        settings=settings,
        store=store or MemoryStore(),
        vector_index=vector_index or MemoryVectorIndex(DeterministicEmbeddings(768)),
        chat_client=FakeChatClient(),
    )
    services.initialize()
    return services


@pytest.fixture
async def runtime():
    services = make_services()
    await services.seed()
    app = create_app(services.settings, services)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client, services.store, services


async def upload_text(
    client: AsyncClient,
    name: str = "requirements.md",
    content: str = "# Requisitos\n\nSupabase armazena vetores.",
):
    return await client.post(
        "/api/v1/ingestion/uploads",
        data={"project_id": "proj-demo"},
        files={"file": (name, content.encode("utf-8"), "text/markdown")},
        headers=AUTH,
    )


@pytest.mark.asyncio
async def test_health_and_seed_create_empty_project(runtime):
    client, _, _ = runtime
    assert (await client.get("/health")).json() == {"status": "ok", "service": "docai"}
    project = await client.get("/api/v1/projects/proj-demo", headers=AUTH)
    materials = await client.get("/api/v1/projects/proj-demo/materials", headers=AUTH)
    assert project.status_code == 200
    assert project.json()["name"] == "DocAI Demo"
    assert materials.json() == {"materials": []}


@pytest.mark.asyncio
async def test_identity_preserves_token_and_membership_contract(runtime):
    client, _, _ = runtime
    accepted = await client.post(
        "/api/v1/identity/tokens/validate",
        json={"token": "dev-token", "project_id": "proj-demo"},
    )
    forbidden = await client.post(
        "/api/v1/identity/tokens/validate",
        json={"token": "dev-token", "project_id": "other"},
    )
    invalid = await client.post(
        "/api/v1/identity/tokens/validate",
        json={"token": "bad-token", "project_id": "proj-demo"},
    )
    assert accepted.status_code == 200
    assert accepted.json()["permissions"] == ["project:read", "material:read", "query:chat"]
    assert forbidden.status_code == 403
    assert invalid.status_code == 401


@pytest.mark.asyncio
async def test_markdown_upload_creates_material_content_and_searchable_chunks(runtime):
    client, _, _ = runtime
    uploaded = await upload_text(client)
    body = uploaded.json()
    content = await client.get(
        f"/api/v1/ingestion/documents/{body['document_id']}/content", headers=AUTH
    )
    materials = await client.get("/api/v1/projects/proj-demo/materials", headers=AUTH)
    results = await client.post(
        "/api/v1/ingestion/search",
        json={"project_id": "proj-demo", "query": "Supabase vetores", "top_k": 5},
        headers=AUTH,
    )
    assert uploaded.status_code == 201
    assert body["status"] == "indexed"
    assert body["chunk_count"] > 0
    assert content.json()["content"].startswith("# Requisitos")
    assert materials.json()["materials"][0]["id"] == body["material_id"]
    assert results.json()["chunks"][0]["file_name"] == "requirements.md"
    assert "#chunk-" not in results.json()["chunks"][0]["location"]


@pytest.mark.asyncio
async def test_delete_material_removes_content_and_retrieval_chunks(runtime):
    client, _, _ = runtime
    uploaded = (await upload_text(client)).json()
    deleted = await client.delete(
        f"/api/v1/projects/proj-demo/materials/{uploaded['material_id']}", headers=AUTH
    )
    materials = await client.get("/api/v1/projects/proj-demo/materials", headers=AUTH)
    content = await client.get(
        f"/api/v1/ingestion/documents/{uploaded['document_id']}/content", headers=AUTH
    )
    results = await client.post(
        "/api/v1/ingestion/search",
        json={"project_id": "proj-demo", "query": "Supabase vetores", "top_k": 5},
        headers=AUTH,
    )
    second_delete = await client.delete(
        f"/api/v1/projects/proj-demo/materials/{uploaded['material_id']}", headers=AUTH
    )
    assert deleted.status_code == 204
    assert materials.json() == {"materials": []}
    assert content.status_code == 404
    assert results.json() == {"chunks": []}
    assert second_delete.status_code == 404
    assert second_delete.json()["detail"]["code"] == "MATERIAL_NOT_FOUND"


@pytest.mark.asyncio
async def test_delete_material_preserves_catalog_if_vector_removal_fails():
    store = MemoryStore()
    services = make_services(store, FailingDeleteVectorIndex(DeterministicEmbeddings(768)))
    await services.seed()
    app = create_app(services.settings, services)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        uploaded = (await upload_text(client)).json()
        response = await client.delete(
            f"/api/v1/projects/proj-demo/materials/{uploaded['material_id']}", headers=AUTH
        )
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "DELETE_INDEX_FAILED"
    assert store.list_materials("proj-demo")[0].id == uploaded["material_id"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("extension", "loader_name"),
    [("pdf", "PyPDFLoader"), ("docx", "Docx2txtLoader")],
)
async def test_binary_upload_types_use_document_loaders(
    runtime, monkeypatch, extension, loader_name
):
    client, _, _ = runtime

    class StubLoader:
        def __init__(self, path):
            assert path.endswith(f".{extension}")

        def load(self):
            return [Document(page_content=f"Conteudo {extension} extraido")]

    monkeypatch.setattr(rag, loader_name, StubLoader)
    response = await client.post(
        "/api/v1/ingestion/uploads",
        data={"project_id": "proj-demo"},
        files={"file": (f"manual.{extension}", b"binary", "application/octet-stream")},
        headers=AUTH,
    )
    assert response.status_code == 201
    assert response.json()["status"] == "indexed"


@pytest.mark.asyncio
async def test_plain_text_upload_is_loaded_and_indexed(runtime):
    client, _, _ = runtime
    response = await client.post(
        "/api/v1/ingestion/uploads",
        data={"project_id": "proj-demo"},
        files={"file": ("notas.txt", b"Texto simples indexado", "text/plain")},
        headers=AUTH,
    )
    assert response.status_code == 201
    assert response.json()["content_type"] == "text/plain"


@pytest.mark.asyncio
async def test_text_json_endpoint_uses_existing_uploaded_material_and_is_idempotent(runtime):
    client, _, _ = runtime
    material_id = (await upload_text(client)).json()["material_id"]
    payload = {
        "project_id": "proj-demo",
        "material_id": material_id,
        "file_name": "second.txt",
        "content": "Persistencia vetorial do novo texto.",
    }
    first = await client.post("/api/v1/ingestion/documents", json=payload, headers=AUTH)
    second = await client.post("/api/v1/ingestion/documents", json=payload, headers=AUTH)
    assert first.status_code == 201
    assert second.json()["document_id"] == first.json()["document_id"]


@pytest.mark.asyncio
async def test_upload_validation_returns_expected_statuses(runtime):
    client, _, services = runtime
    unsupported = await client.post(
        "/api/v1/ingestion/uploads",
        data={"project_id": "proj-demo"},
        files={"file": ("malware.exe", b"x", "application/octet-stream")},
        headers=AUTH,
    )
    empty = await client.post(
        "/api/v1/ingestion/uploads",
        data={"project_id": "proj-demo"},
        files={"file": ("empty.txt", b"", "text/plain")},
        headers=AUTH,
    )
    large = await client.post(
        "/api/v1/ingestion/uploads",
        data={"project_id": "proj-demo"},
        files={
            "file": ("large.txt", b"a" * (services.settings.max_upload_bytes + 1), "text/plain")
        },
        headers=AUTH,
    )
    assert unsupported.status_code == 415
    assert empty.status_code == 422
    assert large.status_code == 413


@pytest.mark.asyncio
async def test_vector_failure_marks_document_failed():
    store = MemoryStore()
    services = make_services(store, FailingVectorIndex(DeterministicEmbeddings(768)))
    await services.seed()
    app = create_app(services.settings, services)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await upload_text(client)
    failed = next(iter(store.documents.values()))
    assert response.status_code == 503
    assert failed.status == "failed"
    assert failed.error_message == "embedding unavailable"
    assert store.list_materials("proj-demo") == []


@pytest.mark.asyncio
async def test_retrieval_filters_by_project(runtime):
    client, store, _ = runtime
    await upload_text(client, "demo.md", "informacao somente demo")
    store.projects["other"] = Project(
        id="other",
        name="Other",
        description="Other",
        created_at=datetime.now(UTC),
    )
    await client.post(
        "/api/v1/ingestion/uploads",
        data={"project_id": "other"},
        files={"file": ("private.md", b"segredo somente outro", "text/markdown")},
        headers=INTERNAL_AUTH,
    )
    result = await client.post(
        "/api/v1/ingestion/search",
        json={"project_id": "proj-demo", "query": "segredo somente outro", "top_k": 5},
        headers=AUTH,
    )
    assert all(chunk["file_name"] != "private.md" for chunk in result.json()["chunks"])


@pytest.mark.asyncio
async def test_chat_requires_upload_then_persists_history_and_feedback(runtime):
    client, store, _ = runtime
    empty = await client.post(
        "/api/v1/query/chat",
        headers=AUTH,
        json={"project_id": "proj-demo", "session_id": "sess-1", "message": "resuma"},
    )
    await upload_text(client)
    response = await client.post(
        "/api/v1/query/chat",
        headers=AUTH,
        json={"project_id": "proj-demo", "session_id": "sess-1", "message": "Supabase"},
    )
    history = await client.get("/api/v1/query/history/sess-1", headers=AUTH)
    feedback = await client.post(
        "/api/v1/query/feedback",
        headers=AUTH,
        json={"session_id": "sess-1", "message_id": "message-1", "rating": "positive"},
    )
    assert empty.status_code == 404
    assert empty.json()["detail"]["code"] == "NO_INDEXED_DOCUMENTS"
    assert response.status_code == 200
    assert response.json()["sources"][0]["file_name"] == "requirements.md"
    assert len(history.json()["turns"]) == 2
    assert feedback.json() == {"accepted": True, "message_id": "message-1"}
    assert store.feedback["message-1"].rating == "positive"


def test_production_requires_external_secrets():
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        build_services(
            Settings(app_env="production", database_url="", groq_api_key="", gemini_api_key="")
        )


def test_production_rejects_supabase_direct_ipv6_database_url():
    with pytest.raises(RuntimeError, match="Session Pooler"):
        build_services(
            Settings(
                app_env="production",
                database_url="postgresql://postgres:secret@db.project.supabase.co:5432/postgres",
                groq_api_key="groq-secret",
                gemini_api_key="gemini-secret",
            )
        )


@pytest.mark.asyncio
async def test_cors_allows_render_static_site_origin(runtime):
    client, _, _ = runtime
    response = await client.options(
        "/api/v1/projects/proj-demo",
        headers={
            "Origin": "https://docai-frontend.onrender.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://docai-frontend.onrender.com"


@pytest.mark.asyncio
async def test_cors_is_preserved_on_unhandled_backend_error():
    store = FailingAppendStore()
    services = make_services(store)
    await services.seed()
    app = create_app(services.settings, services)
    async with AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test"
    ) as client:
        await upload_text(client)
        response = await client.post(
            "/api/v1/query/chat",
            headers={**AUTH, "Origin": "https://docai-frontend-7wym.onrender.com"},
            json={"project_id": "proj-demo", "session_id": "sess-error", "message": "Supabase"},
        )
    assert response.status_code == 500
    assert (
        response.headers["access-control-allow-origin"]
        == "https://docai-frontend-7wym.onrender.com"
    )


def test_migrations_replace_custom_vectors_and_remove_seed_material():
    initial = (Path(__file__).parents[1] / "migrations" / "001_initial.sql").read_text(
        encoding="utf-8"
    )
    upload_migration = (
        Path(__file__).parents[1] / "migrations" / "003_langchain_uploads.sql"
    ).read_text(encoding="utf-8")
    assert "EXTENSION IF NOT EXISTS vector" in initial
    for table in ["projects", "chat_sessions", "feedback", "api_tokens"]:
        assert f"CREATE TABLE IF NOT EXISTS {table}" in initial
    assert "DELETE FROM materials WHERE id = 'mat-architecture'" in upload_migration
    assert "DROP TABLE IF EXISTS document_chunks" in upload_migration
    assert "ADD COLUMN IF NOT EXISTS content_type" in upload_migration
