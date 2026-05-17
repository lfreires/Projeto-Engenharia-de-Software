from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.dependencies import get_ingestion_service
from app.routers.ingestion import router as ingestion_router


def create_app() -> FastAPI:
    get_ingestion_service().reset()
    app = FastAPI(
        title="DocAI Ingestion Service",
        description="Document ingestion and search boundary for the DocAI MVP.",
        version="0.2.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(ingestion_router)
    return app


app = create_app()
