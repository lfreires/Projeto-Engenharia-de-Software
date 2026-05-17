import pytest
from httpx import ASGITransport, AsyncClient

AUTH_HEADER = {"Authorization": "Bearer dev-token"}


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
    response = await client.get("/api/v1/projects/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "projects"}


@pytest.mark.asyncio
async def test_lists_projects(client):
    response = await client.get("/api/v1/projects", headers=AUTH_HEADER)

    assert response.status_code == 200
    projects = response.json()["projects"]
    assert projects[0]["id"] == "proj-demo"
    assert projects[0]["name"] == "DocAI Demo"


@pytest.mark.asyncio
async def test_get_project_by_id(client):
    response = await client.get("/api/v1/projects/proj-demo", headers=AUTH_HEADER)

    assert response.status_code == 200
    assert response.json()["id"] == "proj-demo"


@pytest.mark.asyncio
async def test_unknown_project_returns_404(client):
    response = await client.get("/api/v1/projects/missing", headers=AUTH_HEADER)

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "PROJECT_NOT_FOUND"


@pytest.mark.asyncio
async def test_lists_project_materials(client):
    response = await client.get("/api/v1/projects/proj-demo/materials", headers=AUTH_HEADER)

    assert response.status_code == 200
    materials = response.json()["materials"]
    assert materials[0]["id"] == "mat-architecture"
    assert materials[0]["latest_version"]["version"] == 1
