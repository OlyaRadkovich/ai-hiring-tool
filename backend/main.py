from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
from backend.api.routes import auth, prep, results
from backend.database.connection import connect_to_mongo, close_mongo_connection

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
    app.include_router(auth.router, prefix=f"{settings.api_prefix}/auth", tags=["auth"])
    app.include_router(prep.router, prefix=f"{settings.api_prefix}/prep", tags=["preparation"])
    app.include_router(results.router, prefix=f"{settings.api_prefix}/results", tags=["results"])

    # Database events
    @app.on_event("startup")
    async def startup_db_client():
        await connect_to_mongo()

    @app.on_event("shutdown")
    async def shutdown_db_client():
        await close_mongo_connection()

    return app

app = create_app()


