from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.identity import router as identity_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="DocAI Identity Service",
        description="Dev-token identity and membership service for the DocAI MVP.",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(identity_router)

    return app


app = create_app()
