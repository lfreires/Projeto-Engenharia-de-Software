from unittest.mock import AsyncMock, patch

import pytest

from app.schemas.chat import ChatRequest, HistoryTurn


@pytest.fixture
def valid_request():
    return ChatRequest(
        project_id="proj-1",
        session_id="sess-1",
        message="What is the architecture?",
    )


@pytest.fixture
def mock_chunks():
    return [
        {
            "document_id": "doc-1",
            "file_name": "arch.pdf",
            "chunk_index": 0,
            "chunk_text": "Microservices architecture with 4 services.",
            "@search.score": 0.95,
        }
    ]


@pytest.mark.asyncio
async def test_rag_pipeline_returns_chat_response(valid_request, mock_chunks):
    with (
        patch(
            "app.services.rag_pipeline.search_ingestion",
            new=AsyncMock(return_value=mock_chunks),
        ),
        patch(
            "app.services.rag_pipeline.chat_completion",
            return_value=("The answer.", "llama-3.3-70b-versatile"),
        ),
    ):
        from app.services.rag_pipeline import run
        response = await run(valid_request, history=[])
        assert response.answer == "The answer."
        assert response.session_id == valid_request.session_id
        assert response.model_used == "llama-3.3-70b-versatile"
        assert len(response.sources) == 1
        assert response.latency_ms >= 0


@pytest.mark.asyncio
async def test_rag_pipeline_raises_404_when_no_chunks(valid_request):
    from fastapi import HTTPException

    with (
        patch("app.services.rag_pipeline.search_ingestion", new=AsyncMock(return_value=[])),
    ):
        from app.services.rag_pipeline import run
        with pytest.raises(HTTPException) as exc_info:
            await run(valid_request, history=[])
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_rag_pipeline_passes_history(valid_request, mock_chunks):
    history = [
        HistoryTurn(role="user", content="previous question"),
        HistoryTurn(role="assistant", content="previous answer"),
    ]
    captured_messages = {}

    def capture_chat_completion(messages, model=None):
        captured_messages["messages"] = messages
        return ("ok", "llama-3.3-70b-versatile")

    with (
        patch(
            "app.services.rag_pipeline.search_ingestion",
            new=AsyncMock(return_value=mock_chunks),
        ),
        patch("app.services.rag_pipeline.chat_completion", side_effect=capture_chat_completion),
    ):
        from app.services.rag_pipeline import run
        await run(valid_request, history=history)
        full_text = " ".join(m["content"] for m in captured_messages["messages"])
        assert "previous question" in full_text or "previous answer" in full_text


@pytest.mark.asyncio
async def test_rag_pipeline_calls_ingestion_search_with_project_query_and_top_k(
    valid_request,
    mock_chunks,
):
    search = AsyncMock(return_value=mock_chunks)

    with (
        patch("app.services.rag_pipeline.search_ingestion", new=search),
        patch(
            "app.services.rag_pipeline.chat_completion",
            return_value=("ok", "llama-3.3-70b-versatile"),
        ),
    ):
        from app.services.rag_pipeline import run

        await run(valid_request, history=[])

    search.assert_awaited_once_with(
        project_id=valid_request.project_id,
        query=valid_request.message,
        top_k=valid_request.top_k,
    )
