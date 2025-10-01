import multiprocessing
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from backend.api.routes import prep, results
from backend.core.config import settings
from backend.queue.manager import get_task_queue
from backend.queue.worker import worker

worker_process_state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управляет жизненным циклом фонового воркера.
    """
    logger.info("Приложение запускается...")

    task_queue = get_task_queue()

    p = multiprocessing.Process(target=worker, args=(task_queue,))
    p.start()
    worker_process_state["process"] = p
    logger.info(f"Фоновый воркер запущен с PID: {p.pid}")

    yield

    logger.info("Приложение останавливается...")

    task_queue.put(None)

    p = worker_process_state.get("process")
    if p:
        p.join(timeout=20)
        if p.is_alive():
            logger.warning("Воркер не завершился вовремя, принудительная остановка.")
            p.terminate()
        else:
            logger.info("Фоновый воркер успешно остановлен.")


logger.add("logs/app.log", rotation="500 MB", level="INFO")

app = FastAPI(
    title=settings.app_name,
    description="API для AI-ассистента по проведению интервью.",
    version="1.0.0",
    lifespan=lifespan
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


@app.get("/", summary="Проверка состояния", description="Простой эндпоинт для проверки, что сервер запущен.")
def read_root():
    logger.info("Root endpoint was hit.")
    return {"status": f"{settings.app_name} is running"}


@app.get("/version")
def get_version():
    return {"version": "1.1-cors-fix-check"}
