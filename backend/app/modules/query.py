from fastapi import APIRouter, Depends, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.dependencies import get_services
from app.schemas import (
    ChatRequest,
    ChatResponse,
    FeedbackRequest,
    FeedbackResponse,
    HistoryResponse,
)
from app.services import Services

router = APIRouter(prefix="/api/v1/query", tags=["query"])
security = HTTPBearer(auto_error=False)


def token_value(credentials: HTTPAuthorizationCredentials | None) -> str:
    return credentials.credentials if credentials else ""


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    services: Services = Depends(get_services),
):
    services.authorize(token_value(credentials), request.project_id)
    return await services.chat(request)


@router.post("/feedback", response_model=FeedbackResponse)
async def feedback(
    request: FeedbackRequest,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    services: Services = Depends(get_services),
):
    services.authorize(token_value(credentials))
    return services.feedback(request)


@router.get("/history/{session_id}", response_model=HistoryResponse)
async def history(
    session_id: str,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    services: Services = Depends(get_services),
):
    services.authorize(token_value(credentials))
    return services.history(session_id)


@router.delete("/history/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_history(
    session_id: str,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    services: Services = Depends(get_services),
):
    services.authorize(token_value(credentials))
    services.delete_history(session_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
