from fastapi import APIRouter, Depends, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.dependencies import (
    get_chat_service,
    get_feedback_store,
    get_session_store,
    get_token_validator,
)
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    FeedbackRequest,
    FeedbackResponse,
    HistoryResponse,
)
from app.services.chat_service import ChatService
from app.services.feedback_service import InMemoryFeedbackStore
from app.services.session_service import InMemorySessionStore
from app.services.token_validator import TokenValidator

router = APIRouter()
security = HTTPBearer(auto_error=False)


async def _verify_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    validator: TokenValidator = Depends(get_token_validator),
) -> str:
    if credentials is None:
        return await validator.validate("")
    return await validator.validate(credentials.credentials)


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    _token: str = Depends(_verify_token),
    service: ChatService = Depends(get_chat_service),
):
    return await service.chat(request)


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    _token: str = Depends(_verify_token),
    store: InMemoryFeedbackStore = Depends(get_feedback_store),
):
    return store.submit(request)


@router.get("/history/{session_id}", response_model=HistoryResponse)
async def get_history(
    session_id: str,
    _token: str = Depends(_verify_token),
    sessions: InMemorySessionStore = Depends(get_session_store),
):
    return HistoryResponse(session_id=session_id, turns=sessions.get_history(session_id))


@router.delete("/history/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_history(
    session_id: str,
    _token: str = Depends(_verify_token),
    sessions: InMemorySessionStore = Depends(get_session_store),
):
    sessions.delete_history(session_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
