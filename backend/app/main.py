from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from app.clients import DeterministicEmbeddingClient, GeminiEmbeddingClient, GroqChatClient
from app.config import Settings, settings
from app.modules.identity import router as identity_router
from app.modules.ingestion import router as ingestion_router
from app.modules.projects import router as projects_router
from app.modules.query import router as query_router
from app.services import Services
from app.storage import MemoryStore, PostgresStore


def build_services(configuration: Settings) -> Services:
    if configuration.production:
        missing = [
            name
            for name, value in [
                ("DATABASE_URL", configuration.database_url),
                ("GROQ_API_KEY", configuration.groq_api_key),
                ("GEMINI_API_KEY", configuration.gemini_api_key),
            ]
            if not value
        ]
        if missing:
            raise RuntimeError(f"Production requires environment values: {', '.join(missing)}.")
    store = PostgresStore(configuration) if configuration.database_url else MemoryStore()
    embedding_client = (
        GeminiEmbeddingClient(configuration)
        if configuration.gemini_api_key
        else DeterministicEmbeddingClient(configuration.embedding_dimensions)
    )
    return Services(
        settings=configuration,
        store=store,
        embedding_client=embedding_client,
        chat_client=GroqChatClient(configuration),
    )


def create_app(
    configuration: Settings | None = None,
    injected_services: Services | None = None,
) -> FastAPI:
    configuration = configuration or settings
    services = injected_services or build_services(configuration)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        if isinstance(services.store, PostgresStore) and configuration.run_migrations:
            migrations = Path(__file__).resolve().parent.parent / "migrations"
            services.store.apply_migrations(migrations)
        if configuration.seed_demo_data:
            await services.seed()
        yield

    application = FastAPI(
        title="DocAI",
        description="DocAI monorepo API and frontend runtime for Render.",
        version="2.0.0",
        lifespan=lifespan,
    )
    application.state.services = services
    application.include_router(identity_router)
    application.include_router(projects_router)
    application.include_router(ingestion_router)
    application.include_router(query_router)

    @application.get("/health")
    async def health():
        return {"status": "ok", "service": "docai"}

    @application.get("/{resource_path:path}", include_in_schema=False)
    async def frontend(resource_path: str):
        if resource_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found")
        dist = configuration.frontend_dist.resolve()
        requested = (dist / resource_path).resolve()
        if resource_path and dist in requested.parents and requested.is_file():
            return FileResponse(requested)
        index = dist / "index.html"
        if index.is_file():
            return FileResponse(index)
        raise HTTPException(status_code=404, detail="Frontend build not found.")

    return application


app = create_app()
