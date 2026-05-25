from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.dependencies import get_services
from app.schemas import (
    DocumentContentResponse,
    DocumentCreateRequest,
    DocumentStatusResponse,
    SearchRequest,
    SearchResponse,
)
from app.services import Services

router = APIRouter(prefix="/api/v1/ingestion", tags=["ingestion"])
security = HTTPBearer(auto_error=False)


def token_value(credentials: HTTPAuthorizationCredentials | None) -> str:
    return credentials.credentials if credentials else ""


@router.get("/health")
async def health():
    return {"status": "ok", "service": "ingestion"}


@router.post(
    "/uploads",
    response_model=DocumentStatusResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    project_id: Annotated[str, Form(...)],
    file: Annotated[UploadFile, File(...)],
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    services: Services = Depends(get_services),
):
    services.authorize(token_value(credentials), project_id)
    payload = await file.read(services.settings.max_upload_bytes + 1)
    return await services.upload_document(project_id, file.filename or "", payload)


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


@router.get("/documents/{document_id}/content", response_model=DocumentContentResponse)
async def document_content(
    document_id: str,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    services: Services = Depends(get_services),
):
    services.authorize(token_value(credentials))
    return services.document_content(document_id)


@router.post("/search", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    services: Services = Depends(get_services),
):
    services.authorize(token_value(credentials), request.project_id)
    return await services.search(request)
