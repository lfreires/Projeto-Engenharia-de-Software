from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.query import router as query_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Query Service - RAG Chat",
        description="Modulo de Consulta com RAG (Groq + ingestion-service search)",
        version="1.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(query_router, prefix="/api/v1/query", tags=["query"])

    return app


app = create_app()
