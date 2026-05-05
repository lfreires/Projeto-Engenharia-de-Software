from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.schemas.chat import ChatResponse, SourceItem

# ---- Helpers ----

BASE_URL = "http://test"
AUTH_HEADER = {"Authorization": "Bearer dev-token"}

MOCK_RESPONSE = ChatResponse(
    session_id="sess-1",
    answer="A microservices architecture with 4 services.",
    model_used="llama-3.3-70b-versatile",
    sources=[SourceItem(document_id="d1", file_name="arch.pdf", chunk_index=0, score=0.95)],
    latency_ms=500,
)

MOCK_RESPONSE_FALLBACK = ChatResponse(
    session_id="sess-1",
    answer="Fallback answer.",
    model_used="llama-3.1-8b-instant",
    sources=[SourceItem(document_id="d1", file_name="arch.pdf", chunk_index=0, score=0.95)],
    latency_ms=600,
)

VALID_PAYLOAD = {
    "project_id": "proj-1",
    "session_id": "sess-1",
    "message": "What is the architecture?",
}


@pytest.fixture
def app():
    from app.main import create_app
    return create_app()


@pytest.fixture
async def client(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:
        yield ac


# ---- Health ----

@pytest.mark.asyncio
async def test_health_returns_200(client):
    resp = await client.get("/api/v1/query/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# ---- Chat ----

@pytest.mark.asyncio
async def test_chat_with_valid_payload_returns_200(client):
    with patch("app.routers.query.rag_pipeline.run", return_value=MOCK_RESPONSE):
        resp = await client.post("/api/v1/query/chat", json=VALID_PAYLOAD, headers=AUTH_HEADER)
    assert resp.status_code == 200
    data = resp.json()
    assert data["answer"] == MOCK_RESPONSE.answer
    assert data["model_used"] == "llama-3.3-70b-versatile"
    assert len(data["sources"]) == 1


@pytest.mark.asyncio
async def test_chat_missing_token_returns_401(client):
    resp = await client.post("/api/v1/query/chat", json=VALID_PAYLOAD)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_chat_unknown_project_returns_404(client):
    from fastapi import HTTPException

    with patch(
        "app.routers.query.rag_pipeline.run",
        side_effect=HTTPException(status_code=404, detail={"code": "PROJECT_NOT_FOUND", "message": "not found"}),
    ):
        resp = await client.post("/api/v1/query/chat", json=VALID_PAYLOAD, headers=AUTH_HEADER)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_chat_groq_429_triggers_fallback(client):
    with patch("app.routers.query.rag_pipeline.run", return_value=MOCK_RESPONSE_FALLBACK):
        resp = await client.post("/api/v1/query/chat", json=VALID_PAYLOAD, headers=AUTH_HEADER)
    assert resp.status_code == 200
    assert resp.json()["model_used"] == "llama-3.1-8b-instant"


@pytest.mark.asyncio
async def test_chat_both_models_fail_returns_503(client):
    from fastapi import HTTPException

    with patch(
        "app.routers.query.rag_pipeline.run",
        side_effect=HTTPException(status_code=503, detail={"code": "LLM_UNAVAILABLE", "message": "Groq down"}),
    ):
        resp = await client.post("/api/v1/query/chat", json=VALID_PAYLOAD, headers=AUTH_HEADER)
    assert resp.status_code == 503


# ---- History ----

@pytest.mark.asyncio
async def test_get_history_returns_messages(client):
    # First, post a chat to populate history
    with patch("app.routers.query.rag_pipeline.run", return_value=MOCK_RESPONSE):
        await client.post("/api/v1/query/chat", json=VALID_PAYLOAD, headers=AUTH_HEADER)

    resp = await client.get("/api/v1/query/history/sess-1", headers=AUTH_HEADER)
    assert resp.status_code == 200
    data = resp.json()
    assert data["session_id"] == "sess-1"
    assert len(data["turns"]) >= 2  # user + assistant


@pytest.mark.asyncio
async def test_delete_history_clears_session(client):
    with patch("app.routers.query.rag_pipeline.run", return_value=MOCK_RESPONSE):
        await client.post("/api/v1/query/chat", json=VALID_PAYLOAD, headers=AUTH_HEADER)

    del_resp = await client.delete("/api/v1/query/history/sess-1", headers=AUTH_HEADER)
    assert del_resp.status_code == 204

    hist_resp = await client.get("/api/v1/query/history/sess-1", headers=AUTH_HEADER)
    assert hist_resp.json()["turns"] == []
