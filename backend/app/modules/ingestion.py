from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.dependencies import get_services
from app.schemas import DocumentCreateRequest, DocumentStatusResponse, SearchRequest, SearchResponse
from app.services import Services

router = APIRouter(prefix="/api/v1/ingestion", tags=["ingestion"])
security = HTTPBearer(auto_error=False)


def token_value(credentials: HTTPAuthorizationCredentials | None) -> str:
    return credentials.credentials if credentials else ""


@router.get("/health")
async def health():
    return {"status": "ok", "service": "ingestion"}


@router.post(
    "/documents",
    response_model=DocumentStatusResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_document(
    request: DocumentCreateRequest,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    services: Services = Depends(get_services),
):
    services.authorize(token_value(credentials), request.project_id)
    return await services.index_document(request)


@router.get("/documents/{document_id}/status", response_model=DocumentStatusResponse)
async def document_status(
    document_id: str,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    services: Services = Depends(get_services),
):
    services.authorize(token_value(credentials))
    return services.document_status(document_id)


@router.post("/search", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    services: Services = Depends(get_services),
):
    services.authorize(token_value(credentials), request.project_id)
    return await services.search(request)
