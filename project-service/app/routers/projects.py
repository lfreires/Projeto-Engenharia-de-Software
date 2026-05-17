from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.dependencies import get_catalog_service, get_token_validator
from app.schemas import MaterialsResponse, Project, ProjectsResponse
from app.services.catalog_service import CatalogService, ProjectNotFoundError
from app.services.token_validator import TokenValidator

router = APIRouter(prefix=settings.api_prefix, tags=["projects"])
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


@router.get("", response_model=ProjectsResponse)
async def projects(
    _token: str = Depends(_verify_token),
    service: CatalogService = Depends(get_catalog_service),
):
    return ProjectsResponse(projects=service.list_projects())


@router.get("/{project_id}", response_model=Project)
async def project(
    project_id: str,
    _token: str = Depends(_verify_token),
    service: CatalogService = Depends(get_catalog_service),
):
    try:
        return service.get_project(project_id)
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PROJECT_NOT_FOUND", "message": "Project not found."},
        )


@router.get("/{project_id}/materials", response_model=MaterialsResponse)
async def materials(
    project_id: str,
    _token: str = Depends(_verify_token),
    service: CatalogService = Depends(get_catalog_service),
):
    try:
        return MaterialsResponse(materials=service.get_materials_for_project(project_id))
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PROJECT_NOT_FOUND", "message": "Project not found."},
        )
