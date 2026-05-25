from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp

from app.clients import GroqChatClient
from app.config import Settings, settings
from app.modules.identity import router as identity_router
from app.modules.ingestion import router as ingestion_router
from app.modules.projects import router as projects_router
from app.modules.query import router as query_router
from app.rag import (
    DeterministicEmbeddings,
    LangChainPGVectorIndex,
    MemoryVectorIndex,
    PrefixedGeminiEmbeddings,
)
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
        database_host = (urlparse(configuration.database_url).hostname or "").lower()
        if database_host.startswith("db.") and database_host.endswith(".supabase.co"):
            raise RuntimeError(
                "DATABASE_URL uses the Supabase direct IPv6 endpoint. "
                "Render requires the Supabase Session Pooler or Transaction Pooler URL."
            )
    store = PostgresStore(configuration) if configuration.database_url else MemoryStore()
    vector_index = (
        LangChainPGVectorIndex(configuration, PrefixedGeminiEmbeddings(configuration))
        if configuration.database_url
        else MemoryVectorIndex(DeterministicEmbeddings(configuration.embedding_dimensions))
    )
    return Services(
        settings=configuration,
        store=store,
        vector_index=vector_index,
        chat_client=GroqChatClient(configuration),
    )


def create_app(
    configuration: Settings | None = None,
    injected_services: Services | None = None,
) -> ASGIApp:
    configuration = configuration or settings
    services = injected_services or build_services(configuration)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        if isinstance(services.store, PostgresStore) and configuration.run_migrations:
            migrations = Path(__file__).resolve().parent.parent / "migrations"
            services.store.apply_migrations(migrations)
        services.initialize()
        if configuration.seed_demo_data:
            await services.seed()
        yield

    application = FastAPI(
        title="DocAI",
        description="DocAI consolidated API runtime for Render.",
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

    return CORSMiddleware(
        app=application,
        allow_origins=[
            origin.strip() for origin in configuration.cors_origins.split(",") if origin.strip()
        ],
        allow_origin_regex=configuration.cors_origin_regex or None,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )


app = create_app()
