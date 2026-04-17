from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    FeedbackRequest,
    FeedbackResponse,
    HistoryResponse,
    HistoryTurn,
)
from app.services import rag_pipeline

router = APIRouter()
security = HTTPBearer()

# In-memory session store: session_id -> list of turns
_sessions: dict[str, list[HistoryTurn]] = {}

# In-memory feedback store (message_id -> FeedbackRequest)
_feedback: dict[str, FeedbackRequest] = {}


def _verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Simple Bearer token check. In production, validate JWT from the Auth module."""
    if credentials.credentials != settings.bearer_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Invalid or missing Bearer token"},
        )
    return credentials.credentials


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    _token: str = Depends(_verify_token),
):
    history = _sessions.get(request.session_id, [])

    try:
        response = await rag_pipeline.run(request, history=history)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "LLM_UNAVAILABLE", "message": str(e)},
        )

    # Persist turns to session history
    turns = _sessions.setdefault(request.session_id, [])
    turns.append(HistoryTurn(role="user", content=request.message, timestamp=datetime.utcnow()))
    turns.append(HistoryTurn(role="assistant", content=response.answer, timestamp=datetime.utcnow()))

    return response


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    _token: str = Depends(_verify_token),
):
    """Stores user feedback (thumbs up/down) for a specific AI message.

    Feedback is kept in memory and can be extended to write to storage or a
    monitoring system in future iterations.
    """
    _feedback[request.message_id] = request
    return FeedbackResponse(accepted=True, message_id=request.message_id)


@router.get("/history/{session_id}", response_model=HistoryResponse)
async def get_history(
    session_id: str,
    _token: str = Depends(_verify_token),
):
    turns = _sessions.get(session_id, [])
    return HistoryResponse(session_id=session_id, turns=turns)


@router.delete("/history/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_history(
    session_id: str,
    _token: str = Depends(_verify_token),
):
    _sessions.pop(session_id, None)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
