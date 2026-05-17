import time

from fastapi import HTTPException

from app.schemas.chat import ChatRequest, ChatResponse, HistoryTurn
from app.services.ingestion_client import search_ingestion
from app.services.llm_client import chat_completion
from app.services.prompt_builder import build_messages, format_sources


class RagPipeline:
    async def run(self, request: ChatRequest, history: list[HistoryTurn]) -> ChatResponse:
        start = time.perf_counter()

        chunks = await search_ingestion(
            project_id=request.project_id,
            query=request.message,
            top_k=request.top_k,
        )

        if not chunks:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "PROJECT_NOT_FOUND",
                    "message": f"No documents indexed for project '{request.project_id}'",
                },
            )

        messages = build_messages(
            query=request.message,
            context_chunks=chunks,
            history=history,
        )
        answer, model_used = chat_completion(messages)
        sources = format_sources(chunks)
        latency_ms = int((time.perf_counter() - start) * 1000)

        return ChatResponse(
            session_id=request.session_id,
            answer=answer,
            model_used=model_used,
            sources=sources,
            latency_ms=latency_ms,
        )


_pipeline = RagPipeline()


async def run(request: ChatRequest, history: list[HistoryTurn]) -> ChatResponse:
    return await _pipeline.run(request, history)
