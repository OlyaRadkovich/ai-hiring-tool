import os

from fastapi import FastAPI, status
from loguru import logger
from redis import from_url
from rq import Worker

app = FastAPI(
    title="AI Hiring Tool - On-Demand Worker",
    description="Этот сервис принимает HTTP-запросы для запуска обработки задач из очереди Redis.",
    version="1.0.0"
)

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
conn = from_url(redis_url)
listen_queues = ["results_processing"]


@app.post("/process", status_code=status.HTTP_202_ACCEPTED)
def trigger_processing():
    """
    Этот эндпоинт принимает 'пинок' от основного бэкенда
    и запускает обработку очереди в режиме 'burst'.
    """
    logger.info("Получен триггер, запускаю обработку очереди...")
    if not conn:
        logger.error("Нет подключения к Redis. Обработка невозможна.")
        return {"status": "error", "detail": "Redis connection not available"}

    try:
        worker = Worker(queues=listen_queues, connection=conn)

        did_process_anything = worker.work(burst=True)

        logger.info(f"Обработка очереди завершена. Были ли обработаны задачи: {did_process_anything}")
        return {"status": "ok", "processed": did_process_anything}

    except Exception as e:
        logger.error(f"Ошибка при обработке очереди: {e}", exc_info=True)
        return {"status": "error", "detail": str(e)}
