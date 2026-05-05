from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.query import router as query_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-load sentence-transformers model on startup to avoid cold start
    try:
        from app.services.embedder import _get_model
        _get_model()
    except Exception:
        pass  # In test/CI environments the model may be mocked
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Query Service — RAG Chat",
        description="Módulo de Consulta com RAG (Groq + sentence-transformers + Azure AI Search)",
        version="1.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Tighten in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(query_router, prefix="/api/v1/query", tags=["query"])

    return app


app = create_app()
