import multiprocessing
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from backend.api.routes import prep, results
from backend.core.config import settings
from backend.queue.manager import get_task_queue
from backend.queue.worker import worker

worker_processes_state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the lifecycle of the background worker pool.
    """
    logger.info("Application starting up...")

    num_workers = os.cpu_count() or 2
    logger.info(f"Starting {num_workers} worker processes.")

    task_queue = get_task_queue()
    processes = []

    for i in range(num_workers):
        process_name = f"Worker-{i + 1}"
        p = multiprocessing.Process(target=worker, args=(task_queue,), name=process_name)
        p.start()
        processes.append(p)
        logger.info(f"Started worker process {p.name} with PID: {p.pid}")

    worker_processes_state["processes"] = processes

    yield

    logger.info("Application shutting down...")
    processes = worker_processes_state.get("processes", [])
    if processes:
        logger.info("Sending shutdown signal to all workers...")

        for _ in processes:
            task_queue.put(None)

        for p in processes:
            p.join(timeout=20)
            if p.is_alive():
                logger.warning(f"Worker {p.name} did not shut down gracefully. Terminating.")
                p.terminate()
            else:
                logger.info(f"Worker {p.name} shut down successfully.")


logger.add("logs/app.log", rotation="500 MB", level="INFO")

app = FastAPI(
    title=settings.app_name,
    description="API for AI-assistant for interviews.",
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


@app.get("/", summary="Health Check", description="A simple endpoint to check if the server is running.")
def read_root():
    logger.info("Root endpoint was hit.")
    return {"status": f"{settings.app_name} is running"}


@app.get("/version")
def get_version():
    return {"version": "1.1-cors-fix-check"}