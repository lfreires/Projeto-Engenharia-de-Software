from fastapi import HTTPException, status

from app.schemas.chat import ChatRequest, ChatResponse
from app.services import rag_pipeline
from app.services.session_service import InMemorySessionStore


class ChatService:
    def __init__(self, sessions: InMemorySessionStore) -> None:
        self._sessions = sessions

    async def chat(self, request: ChatRequest) -> ChatResponse:
        history = self._sessions.get_history(request.session_id)

        try:
            response = await rag_pipeline.run(request, history=history)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"code": "LLM_UNAVAILABLE", "message": str(exc)},
            )

        self._sessions.append_turns(
            session_id=request.session_id,
            user_message=request.message,
            assistant_answer=response.answer,
        )
        return response
