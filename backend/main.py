from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api.routes import prep, results


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        openapi_url=f"{settings.api_prefix}/openapi.json"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoint
    @app.get(f"{settings.api_prefix}/health")
    def health() -> dict:
        return {"status": "ok"}

    # Include API routes
    app.include_router(prep.router, prefix=f"{settings.api_prefix}/prep", tags=["preparation"])
    app.include_router(results.router, prefix=f"{settings.api_prefix}/results", tags=["results"])

    return app


app = create_app()
