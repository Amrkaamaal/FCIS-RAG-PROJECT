import os

from fastapi import FastAPI

from routes import router as api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=os.getenv("APP_NAME", "RAG Project")
    )

    app.include_router(api_router)

    return app


app = create_app()