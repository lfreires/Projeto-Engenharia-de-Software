from typing import Protocol

from app.schemas import MembershipItem, UserItem

PROJECT_PERMISSIONS = ["project:read", "material:read", "query:chat"]


class IdentityRepository(Protocol):
    def get_token(self, token: str) -> dict[str, object] | None:
        raise NotImplementedError

    def list_users(self) -> list[UserItem]:
        raise NotImplementedError

    def list_memberships(self, project_id: str | None = None) -> list[MembershipItem]:
        raise NotImplementedError


class InMemoryIdentityRepository:
    def __init__(self) -> None:
        self._users = [
            UserItem(id="user-demo", email="demo@docai.local", display_name="Demo User"),
        ]
        self._memberships = [
            MembershipItem(
                project_id="proj-demo",
                user_id="user-demo",
                role="owner",
                permissions=PROJECT_PERMISSIONS,
            ),
        ]
        self._tokens: dict[str, dict[str, object]] = {
            "dev-token": {
                "subject_id": "user-demo",
                "subject_type": "user",
                "permissions": PROJECT_PERMISSIONS,
            },
            "internal-query-token": {
                "subject_id": "query-service",
                "subject_type": "service",
                "permissions": ["ingestion:search", "identity:validate"],
            },
        }

    def get_token(self, token: str) -> dict[str, object] | None:
        return self._tokens.get(token)

    def list_users(self) -> list[UserItem]:
        return list(self._users)

    def list_memberships(self, project_id: str | None = None) -> list[MembershipItem]:
        if project_id is None:
            return list(self._memberships)
        return [
            membership
            for membership in self._memberships
            if membership.project_id == project_id
        ]
