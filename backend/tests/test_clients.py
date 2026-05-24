import httpx
import pytest

from app.clients import GeminiEmbeddingClient, GroqChatClient
from app.config import Settings


class StubAsyncClient:
    requests = []
    responses = []

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def post(self, url, **kwargs):
        self.requests.append((url, kwargs))
        return self.responses.pop(0)


@pytest.mark.asyncio
async def test_gemini_uses_retrieval_task_and_validates_dimensions(monkeypatch):
    StubAsyncClient.requests = []
    StubAsyncClient.responses = [
        httpx.Response(
            200,
            request=httpx.Request("POST", "https://generativelanguage.googleapis.com"),
            json={"embedding": {"values": [0.25, 0.75]}},
        )
    ]
    monkeypatch.setattr(httpx, "AsyncClient", StubAsyncClient)
    client = GeminiEmbeddingClient(
        Settings(
            gemini_api_key="secret",
            embedding_dimensions=2,
            embedding_model="gemini-embedding-001",
        )
    )

    vector = await client.embed_query("consulta")

    assert vector == [0.25, 0.75]
    assert StubAsyncClient.requests[0][1]["json"]["taskType"] == "RETRIEVAL_QUERY"


@pytest.mark.asyncio
async def test_groq_falls_back_after_rate_limit(monkeypatch):
    request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    StubAsyncClient.requests = []
    StubAsyncClient.responses = [
        httpx.Response(429, request=request),
        httpx.Response(
            200,
            request=request,
            json={"choices": [{"message": {"content": "fallback"}}]},
        ),
    ]
    monkeypatch.setattr(httpx, "AsyncClient", StubAsyncClient)
    client = GroqChatClient(Settings(groq_api_key="secret"))

    answer, model = await client.complete([{"role": "user", "content": "ola"}])

    assert answer == "fallback"
    assert model == "llama-3.1-8b-instant"
