from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from app.clients import DeterministicEmbeddingClient
from app.config import Settings
from app.main import build_services, create_app
from app.services import Services
from app.storage import MemoryStore

AUTH = {"Authorization": "Bearer dev-token"}
INTERNAL_AUTH = {"Authorization": "Bearer internal-query-token"}


class FakeChatClient:
    async def complete(self, messages):
        assert any("Supabase" in message["content"] for message in messages)
        return "O DocAI armazena vetores no Supabase.", "fake-groq-model"


@pytest.fixture
async def runtime(tmp_path):
    settings = Settings(
        seed_demo_data=False,
        embedding_dimensions=768,
    )
    store = MemoryStore()
    services = Services(
        settings=settings,
        store=store,
        embedding_client=DeterministicEmbeddingClient(768),
        chat_client=FakeChatClient(),
    )
    await services.seed()
    app = create_app(settings, services)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client, store


@pytest.mark.asyncio
async def test_health_and_seed_catalog_are_available(runtime):
    client, _ = runtime
    assert (await client.get("/health")).json() == {"status": "ok", "service": "docai"}

    project = await client.get("/api/v1/projects/proj-demo", headers=AUTH)
    materials = await client.get("/api/v1/projects/proj-demo/materials", headers=AUTH)

    assert project.status_code == 200
    assert project.json()["name"] == "DocAI Demo"
    assert materials.json()["materials"][0]["latest_version"]["document_id"].startswith("doc-")


@pytest.mark.asyncio
async def test_identity_preserves_token_and_membership_contract(runtime):
    client, _ = runtime
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
async def test_document_index_is_idempotent_and_searchable(runtime):
    client, _ = runtime
    payload = {
        "project_id": "proj-demo",
        "material_id": "mat-architecture",
        "file_name": "new.md",
        "content": "Supabase armazena vetores persistentes para busca RAG.",
    }
    first = await client.post("/api/v1/ingestion/documents", json=payload, headers=AUTH)
    second = await client.post("/api/v1/ingestion/documents", json=payload, headers=AUTH)
    results = await client.post(
        "/api/v1/ingestion/search",
        json={"project_id": "proj-demo", "query": "Supabase vetores", "top_k": 5},
        headers=AUTH,
    )

    assert first.status_code == 201
    assert second.json()["document_id"] == first.json()["document_id"]
    assert any(chunk["file_name"] == "new.md" for chunk in results.json()["chunks"])


@pytest.mark.asyncio
async def test_document_index_rejects_unknown_material(runtime):
    client, _ = runtime
    response = await client.post(
        "/api/v1/ingestion/documents",
        headers=AUTH,
        json={
            "project_id": "proj-demo",
            "material_id": "missing",
            "file_name": "missing.md",
            "content": "documento",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "MATERIAL_NOT_FOUND"


@pytest.mark.asyncio
async def test_chat_history_and_feedback_persist_through_store(runtime):
    client, store = runtime
    response = await client.post(
        "/api/v1/query/chat",
        headers=AUTH,
        json={"project_id": "proj-demo", "session_id": "sess-1", "message": "Supabase vetores"},
    )
    history = await client.get("/api/v1/query/history/sess-1", headers=AUTH)
    feedback = await client.post(
        "/api/v1/query/feedback",
        headers=AUTH,
        json={"session_id": "sess-1", "message_id": "message-1", "rating": "positive"},
    )

    assert response.status_code == 200
    assert response.json()["sources"]
    assert len(history.json()["turns"]) == 2
    assert feedback.json() == {"accepted": True, "message_id": "message-1"}
    assert store.feedback["message-1"].rating == "positive"


@pytest.mark.asyncio
async def test_internal_token_can_search_without_user_membership(runtime):
    client, _ = runtime
    result = await client.post(
        "/api/v1/ingestion/search",
        headers=INTERNAL_AUTH,
        json={"project_id": "no-membership", "query": "anything", "top_k": 1},
    )

    assert result.status_code == 200
    assert result.json() == {"chunks": []}


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
    client, _ = runtime
    response = await client.options(
        "/api/v1/projects/proj-demo",
        headers={
            "Origin": "https://docai-frontend.onrender.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == (
        "https://docai-frontend.onrender.com"
    )


def test_migration_defines_vector_and_persistent_domains():
    migration = (Path(__file__).parents[1] / "migrations" / "001_initial.sql").read_text(
        encoding="utf-8"
    )
    assert "EXTENSION IF NOT EXISTS vector" in migration
    assert "embedding extensions.vector(768)" in migration
    for table in ["projects", "document_chunks", "chat_sessions", "feedback", "api_tokens"]:
        assert f"CREATE TABLE IF NOT EXISTS {table}" in migration
