from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.config import settings
from app.dependencies import get_identity_service
from app.schemas import (
    MembershipsResponse,
    TokenValidationRequest,
    TokenValidationResponse,
    UsersResponse,
)
from app.services.identity_service import (
    IdentityService,
    InvalidTokenError,
    ProjectForbiddenError,
)

router = APIRouter(prefix=settings.api_prefix, tags=["identity"])


@router.get("/health")
async def health():
    return {"status": "ok", "service": settings.service_name}


@router.post("/tokens/validate", response_model=TokenValidationResponse)
async def validate(
    request: TokenValidationRequest,
    service: IdentityService = Depends(get_identity_service),
):
    try:
        return service.validate_token(request.token, project_id=request.project_id)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Token is invalid or inactive."},
        )
    except ProjectForbiddenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "PROJECT_FORBIDDEN",
                "message": "Token subject is not a member of this project.",
            },
        )


@router.get("/users", response_model=UsersResponse)
async def users(service: IdentityService = Depends(get_identity_service)):
    return UsersResponse(users=service.list_users())


@router.get("/memberships", response_model=MembershipsResponse)
async def memberships(
    project_id: str | None = Query(default=None),
    service: IdentityService = Depends(get_identity_service),
):
    return MembershipsResponse(memberships=service.list_memberships(project_id))
