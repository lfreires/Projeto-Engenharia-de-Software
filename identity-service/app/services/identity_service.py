from typing import cast

from app.repositories.identity_repository import IdentityRepository
from app.schemas import MembershipItem, TokenValidationResponse, UserItem


class InvalidTokenError(Exception):
    pass


class ProjectForbiddenError(Exception):
    pass


class IdentityService:
    def __init__(self, repository: IdentityRepository) -> None:
        self._repository = repository

    def list_users(self) -> list[UserItem]:
        return self._repository.list_users()

    def list_memberships(self, project_id: str | None = None) -> list[MembershipItem]:
        return self._repository.list_memberships(project_id)

    def validate_token(self, token: str, project_id: str | None) -> TokenValidationResponse:
        token_data = self._repository.get_token(token)
        if token_data is None:
            raise InvalidTokenError()

        subject_id = cast(str, token_data["subject_id"])
        subject_type = cast(str, token_data["subject_type"])
        permissions = cast(list[str], token_data["permissions"])

        if project_id and subject_type == "user":
            memberships = self._repository.list_memberships(project_id)
            has_membership = any(membership.user_id == subject_id for membership in memberships)
            if not has_membership:
                raise ProjectForbiddenError()

        return TokenValidationResponse(
            active=True,
            subject_id=subject_id,
            subject_type=subject_type,
            project_id=project_id,
            permissions=list(permissions),
        )
