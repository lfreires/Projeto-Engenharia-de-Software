from fastapi import APIRouter, Depends, Query

from app.dependencies import get_services
from app.schemas import (
    MembershipsResponse,
    TokenValidationRequest,
    TokenValidationResponse,
    UsersResponse,
)
from app.services import Services

router = APIRouter(prefix="/api/v1/identity", tags=["identity"])


@router.get("/health")
async def health():
    return {"status": "ok", "service": "identity"}


@router.post("/tokens/validate", response_model=TokenValidationResponse)
async def validate(
    request: TokenValidationRequest,
    services: Services = Depends(get_services),
):
    return services.validate_identity_token(request.token, request.project_id)


@router.get("/users", response_model=UsersResponse)
async def users(services: Services = Depends(get_services)):
    return services.list_users()


@router.get("/memberships", response_model=MembershipsResponse)
async def memberships(
    project_id: str | None = Query(default=None),
    services: Services = Depends(get_services),
):
    return services.list_memberships(project_id)
