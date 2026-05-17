from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.dependencies import get_ingestion_service, get_token_validator
from app.schemas import (
    DocumentCreateRequest,
    DocumentStatusResponse,
    SearchChunk,
    SearchRequest,
    SearchResponse,
)
from app.services.ingestion_service import DocumentNotFoundError, IngestionService
from app.services.token_validator import TokenValidator

router = APIRouter(prefix=settings.api_prefix, tags=["ingestion"])
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
    return {"status": "ok", "service": settings.service_name}


@router.post(
    "/documents",
    response_model=DocumentStatusResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_document(
    request: DocumentCreateRequest,
    _token: str = Depends(_verify_token),
    service: IngestionService = Depends(get_ingestion_service),
):
    return service.index_document(
        project_id=request.project_id,
        material_id=request.material_id,
        file_name=request.file_name,
        content=request.content,
    )


@router.get("/documents/{document_id}/status", response_model=DocumentStatusResponse)
async def document_status(
    document_id: str,
    _token: str = Depends(_verify_token),
    service: IngestionService = Depends(get_ingestion_service),
):
    try:
        return service.get_document_status(document_id)
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DOCUMENT_NOT_FOUND", "message": "Document not found."},
        )


@router.post("/search", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    _token: str = Depends(_verify_token),
    service: IngestionService = Depends(get_ingestion_service),
):
    chunks = service.search(project_id=request.project_id, query=request.query, top_k=request.top_k)
    return SearchResponse(chunks=[SearchChunk(**chunk.__dict__) for chunk in chunks])
