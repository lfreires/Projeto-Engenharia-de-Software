import os

import pytest

from app.schemas.chat import ChatRequest
from app.services.rag_pipeline import RagPipeline

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_REAL_GROQ_E2E") != "true" or not os.getenv("GROQ_API_KEY"),
    reason="Set RUN_REAL_GROQ_E2E=true and GROQ_API_KEY to run the real Groq E2E test.",
)


@pytest.mark.asyncio
async def test_real_groq_rag_answer_includes_retrieved_file_location(monkeypatch):
    chunks = [
        {
            "document_id": "doc-real-e2e",
            "project_id": "proj-demo",
            "material_id": "mat-architecture",
            "file_name": "architecture.md",
            "location": "architecture.md#chunk-7",
            "chunk_index": 7,
            "chunk_text": (
                "DocAI is split into identity-service, project-service, "
                "ingestion-service, query-service, and frontend. "
                "The query-service calls ingestion-service search instead of AI Search directly."
            ),
            "@search.score": 0.99,
        }
    ]

    async def fake_search_ingestion(project_id: str, query: str, top_k: int):
        return chunks

    monkeypatch.setattr("app.services.rag_pipeline.search_ingestion", fake_search_ingestion)

    response = await RagPipeline().run(
        ChatRequest(
            project_id="proj-demo",
            session_id="sess-real-groq",
            message="Quais servicos compoem o DocAI e onde essa informacao foi recuperada?",
            top_k=1,
        ),
        history=[],
    )

    assert response.answer
    assert response.model_used
    assert response.sources[0].location == "architecture.md#chunk-7"
    assert "architecture.md" in response.answer or "chunk-7" in response.answer
