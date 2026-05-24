from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.dependencies import get_services
from app.schemas import MaterialsResponse, Project, ProjectsResponse
from app.services import Services

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])
security = HTTPBearer(auto_error=False)


def token_value(credentials: HTTPAuthorizationCredentials | None) -> str:
    return credentials.credentials if credentials else ""


@router.get("/health")
async def health():
    return {"status": "ok", "service": "projects"}


@router.get("", response_model=ProjectsResponse)
async def projects(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    services: Services = Depends(get_services),
):
    services.authorize(token_value(credentials))
    return services.list_projects()


@router.get("/{project_id}", response_model=Project)
async def project(
    project_id: str,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    services: Services = Depends(get_services),
):
    services.authorize(token_value(credentials), project_id)
    return services.get_project(project_id)


@router.get("/{project_id}/materials", response_model=MaterialsResponse)
async def materials(
    project_id: str,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    services: Services = Depends(get_services),
):
    services.authorize(token_value(credentials), project_id)
    return services.list_materials(project_id)
