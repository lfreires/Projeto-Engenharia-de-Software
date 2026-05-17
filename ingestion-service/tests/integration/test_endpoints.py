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
    response = await client.get("/api/v1/ingestion/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "ingestion"}


@pytest.mark.asyncio
async def test_create_document_indexes_chunks(client):
    response = await client.post(
        "/api/v1/ingestion/documents",
        headers=AUTH_HEADER,
        json={
            "project_id": "proj-demo",
            "material_id": "mat-architecture",
            "file_name": "architecture.pdf",
            "content": "DocAI uses identity, project, ingestion and query services.",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["document_id"].startswith("doc-")
    assert body["status"] == "indexed"
    assert body["chunk_count"] == 1


@pytest.mark.asyncio
async def test_document_status_returns_indexed_document(client):
    created = await client.post(
        "/api/v1/ingestion/documents",
        headers=AUTH_HEADER,
        json={
            "project_id": "proj-demo",
            "material_id": "mat-architecture",
            "file_name": "architecture.pdf",
            "content": "A document about Azure API Management.",
        },
    )
    document_id = created.json()["document_id"]

    response = await client.get(
        f"/api/v1/ingestion/documents/{document_id}/status",
        headers=AUTH_HEADER,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "indexed"


@pytest.mark.asyncio
async def test_search_returns_contract_chunks(client):
    await client.post(
        "/api/v1/ingestion/documents",
        headers=AUTH_HEADER,
        json={
            "project_id": "proj-demo",
            "material_id": "mat-architecture",
            "file_name": "architecture.pdf",
            "content": "The query service calls ingestion search instead of AI Search directly.",
        },
    )

    response = await client.post(
        "/api/v1/ingestion/search",
        headers=AUTH_HEADER,
        json={"project_id": "proj-demo", "query": "Who calls ingestion search?", "top_k": 3},
    )

    assert response.status_code == 200
    chunks = response.json()["chunks"]
    assert chunks[0]["material_id"] == "mat-architecture"
    assert chunks[0]["file_name"] == "architecture.pdf"
    assert chunks[0]["chunk_index"] == 0
    assert chunks[0]["score"] > 0


@pytest.mark.asyncio
async def test_search_filters_by_project(client):
    await client.post(
        "/api/v1/ingestion/documents",
        headers=AUTH_HEADER,
        json={
            "project_id": "proj-demo",
            "material_id": "mat-architecture",
            "file_name": "architecture.pdf",
            "content": "Visible content.",
        },
    )

    response = await client.post(
        "/api/v1/ingestion/search",
        headers=AUTH_HEADER,
        json={"project_id": "other-project", "query": "Visible", "top_k": 3},
    )

    assert response.status_code == 200
    assert response.json() == {"chunks": []}
