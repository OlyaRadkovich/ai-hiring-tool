from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings
from backend.api.routes import auth, prep, results


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        openapi_url=f"{settings.api_prefix}/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get(f"{settings.api_prefix}/health")
    def health() -> dict:
        return {"status": "ok"}

    api = FastAPI()
    app.include_router(auth.router, prefix=settings.api_prefix)
    app.include_router(prep.router, prefix=settings.api_prefix)
    app.include_router(results.router, prefix=settings.api_prefix)

    return app


app = create_app()


