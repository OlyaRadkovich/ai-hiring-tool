from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from backend.api.routes import prep, results
from backend.core.config import settings

logger.add("logs/app.log", rotation="500 MB", level="INFO")

app = FastAPI(
    title=settings.app_name,
    description="API for AI-assistant for interviews.",
    version="1.0.0",
)

origins = [
    "https://ai-hiring-tool-frontend-1053066596162.europe-west1.run.app",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prep.router, prefix="/api/prep", tags=["Interview Preparation"])
app.include_router(results.router, prefix="/api/results", tags=["Interview Results"])


@app.get("/", summary="Health Check", description="A simple endpoint to check if the server is running.")
def read_root():
    logger.info("Root endpoint was hit.")
    return {"status": f"{settings.app_name} is running"}


@app.get("/version")
def get_version():
    return {"version": "1.1-cors-fix-check"}