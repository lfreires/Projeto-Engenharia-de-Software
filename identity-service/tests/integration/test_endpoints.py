import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def app():
    from app.main import create_app

    return create_app()


@pytest.fixture
async def client(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_returns_ok(client):
    response = await client.get("/api/v1/identity/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "identity"}


@pytest.mark.asyncio
async def test_validate_accepts_known_dev_token(client):
    response = await client.post(
        "/api/v1/identity/tokens/validate",
        json={"token": "dev-token", "project_id": "proj-demo"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "active": True,
        "subject_id": "user-demo",
        "subject_type": "user",
        "project_id": "proj-demo",
        "permissions": ["project:read", "material:read", "query:chat"],
    }


@pytest.mark.asyncio
async def test_validate_rejects_unknown_token(client):
    response = await client.post(
        "/api/v1/identity/tokens/validate",
        json={"token": "wrong", "project_id": "proj-demo"},
    )

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_TOKEN"


@pytest.mark.asyncio
async def test_validate_rejects_project_without_membership(client):
    response = await client.post(
        "/api/v1/identity/tokens/validate",
        json={"token": "dev-token", "project_id": "proj-private"},
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "PROJECT_FORBIDDEN"


@pytest.mark.asyncio
async def test_lists_demo_users(client):
    response = await client.get("/api/v1/identity/users")

    assert response.status_code == 200
    assert response.json()["users"][0]["id"] == "user-demo"


@pytest.mark.asyncio
async def test_lists_memberships_for_project(client):
    response = await client.get("/api/v1/identity/memberships", params={"project_id": "proj-demo"})

    assert response.status_code == 200
    assert response.json()["memberships"] == [
        {
            "project_id": "proj-demo",
            "user_id": "user-demo",
            "role": "owner",
            "permissions": ["project:read", "material:read", "query:chat"],
        }
    ]
