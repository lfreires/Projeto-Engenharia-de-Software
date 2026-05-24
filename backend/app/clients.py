import hashlib
from collections.abc import Sequence

import httpx

from app.config import Settings


class GeminiEmbeddingClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def embed_document(self, text: str) -> list[float]:
        return await self._embed(text, "RETRIEVAL_DOCUMENT")

    async def embed_query(self, text: str) -> list[float]:
        return await self._embed(text, "RETRIEVAL_QUERY")

    async def _embed(self, text: str, task_type: str) -> list[float]:
        if not self._settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is required to generate embeddings.")
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self._settings.embedding_model}:embedContent"
        )
        payload = {
            "model": f"models/{self._settings.embedding_model}",
            "content": {"parts": [{"text": text}]},
            "taskType": task_type,
            "outputDimensionality": self._settings.embedding_dimensions,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                params={"key": self._settings.gemini_api_key},
                json=payload,
            )
            response.raise_for_status()
        values = response.json()["embedding"]["values"]
        if len(values) != self._settings.embedding_dimensions:
            raise RuntimeError("Gemini returned an unexpected embedding dimension.")
        return [float(value) for value in values]


class DeterministicEmbeddingClient:
    """Small local fallback used only outside production and in tests."""

    def __init__(self, dimensions: int) -> None:
        self._dimensions = dimensions

    async def embed_document(self, text: str) -> list[float]:
        return self._embed(text)

    async def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        values = [0.0] * self._dimensions
        for token in text.lower().split():
            slot = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16) % self._dimensions
            values[slot] += 1.0
        return values


class GroqChatClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def complete(self, messages: Sequence[dict[str, str]]) -> tuple[str, str]:
        try:
            return await self._complete(messages, self._settings.primary_llm_model)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code != 429:
                raise
            return await self._complete(messages, self._settings.fallback_llm_model)

    async def _complete(
        self,
        messages: Sequence[dict[str, str]],
        model: str,
    ) -> tuple[str, str]:
        if not self._settings.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is required to answer chat requests.")
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self._settings.groq_api_key}"},
                json={
                    "model": model,
                    "messages": list(messages),
                    "temperature": 0,
                    "max_tokens": 1024,
                },
            )
            response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"], model
