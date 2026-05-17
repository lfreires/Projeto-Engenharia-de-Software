from app.dependencies import get_identity_service
from app.schemas import MembershipItem, TokenValidationResponse, UserItem
from app.services.identity_service import (
    InvalidTokenError as InvalidTokenError,
)
from app.services.identity_service import (
    ProjectForbiddenError as ProjectForbiddenError,
)


def list_users() -> list[UserItem]:
    return get_identity_service().list_users()


def list_memberships(project_id: str | None = None) -> list[MembershipItem]:
    return get_identity_service().list_memberships(project_id)


def validate_token(token: str, project_id: str | None) -> TokenValidationResponse:
    return get_identity_service().validate_token(token, project_id)
