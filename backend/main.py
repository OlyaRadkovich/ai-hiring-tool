from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # 1. Импортируем CORSMiddleware
from loguru import logger
from backend.api.routes import prep, results
from backend.core.config import settings

logger.add("logs/app.log", rotation="500 MB", level="INFO")

app = FastAPI(
    title=settings.app_name,
    description="API для AI-ассистента по проведению интервью.",
    version="1.0.0"
)

origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prep.router, prefix="/api/prep", tags=["Interview Preparation"])
app.include_router(results.router, prefix="/api/results", tags=["Interview Results"])


@app.get("/", summary="Проверка состояния", description="Простой эндпоинт для проверки, что сервер запущен.")
def read_root():
    logger.info("Root endpoint was hit.")
    return {"status": f"{settings.app_name} is running"}
