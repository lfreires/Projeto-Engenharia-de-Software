from pydantic import BaseModel, Field


class TokenValidationRequest(BaseModel):
    token: str = Field(..., min_length=1)
    project_id: str | None = None


class TokenValidationResponse(BaseModel):
    active: bool
    subject_id: str
    subject_type: str
    project_id: str | None
    permissions: list[str]


class UserItem(BaseModel):
    id: str
    email: str
    display_name: str


class UsersResponse(BaseModel):
    users: list[UserItem]


class MembershipItem(BaseModel):
    project_id: str
    user_id: str
    role: str
    permissions: list[str]


class MembershipsResponse(BaseModel):
    memberships: list[MembershipItem]
