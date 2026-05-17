import pytest

from app.domain import InvalidTokenError, ProjectForbiddenError, validate_token


def test_validate_token_returns_subject_and_permissions():
    result = validate_token("dev-token", project_id="proj-demo")

    assert result.active is True
    assert result.subject_id == "user-demo"
    assert result.permissions == ["project:read", "material:read", "query:chat"]


def test_validate_token_allows_internal_service_client():
    result = validate_token("internal-query-token", project_id=None)

    assert result.active is True
    assert result.subject_id == "query-service"
    assert result.subject_type == "service"
    assert "ingestion:search" in result.permissions


def test_validate_token_rejects_unknown_token():
    with pytest.raises(InvalidTokenError):
        validate_token("unknown", project_id=None)


def test_validate_token_checks_project_membership():
    with pytest.raises(ProjectForbiddenError):
        validate_token("dev-token", project_id="proj-private")
