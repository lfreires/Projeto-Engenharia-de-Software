import time

from fastapi import HTTPException

from app.schemas.chat import ChatRequest, ChatResponse, HistoryTurn
from app.services.embedder import embed
from app.services.llm_client import chat_completion
from app.services.prompt_builder import build_messages, format_sources
from app.services.retriever import retrieve


async def run(request: ChatRequest, history: list[HistoryTurn]) -> ChatResponse:
    """Execute the full RAG pipeline following PRD §3.3."""
    start = time.perf_counter()

    # Step 2: Generate embedding locally
    embedding = embed(request.message)

    # Step 3: Retrieve top-k chunks filtered by project_id
    chunks = retrieve(embedding, project_id=request.project_id, top_k=request.top_k)

    # Step 4+: Raise 404 if no documents are indexed for this project
    if not chunks:
        raise HTTPException(
            status_code=404,
            detail={"code": "PROJECT_NOT_FOUND", "message": f"No documents indexed for project '{request.project_id}'"},
        )

    # Step 5: Build prompt with context + history
    messages = build_messages(
        query=request.message,
        context_chunks=chunks,
        history=history,
    )

    # Step 6+7: Call LLM (with automatic fallback on 429)
    answer, model_used = chat_completion(messages)

    # Step 8: Format sources
    sources = format_sources(chunks)

    latency_ms = int((time.perf_counter() - start) * 1000)

    return ChatResponse(
        session_id=request.session_id,
        answer=answer,
        model_used=model_used,
        sources=sources,
        latency_ms=latency_ms,
    )
