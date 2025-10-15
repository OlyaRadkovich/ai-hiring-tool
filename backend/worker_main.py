import os
import subprocess
from fastapi import FastAPI, status
from loguru import logger

app = FastAPI(
    title="AI Hiring Tool - On-Demand Worker",
    description="Этот сервис принимает HTTP-запросы для запуска обработки задач из очереди Redis.",
    version="1.0.0"
)

redis_url = os.getenv('REDIS_URL')
listen_queues = ["results_processing"]


@app.post("/process", status_code=status.HTTP_202_ACCEPTED)
def trigger_processing():
    """
    Этот эндпоинт принимает 'пинок' и запускает обработку очереди в отдельном процессе.
    """
    logger.info("Получен триггер, запускаю обработку очереди в отдельном процессе...")
    if not redis_url:
        logger.error("Нет REDIS_URL. Обработка невозможна.")
        return {"status": "error", "detail": "Redis URL not configured"}

    try:
        command = [
            "rq", "worker",
            "--burst",
            "--url", redis_url,
            *listen_queues
        ]
        subprocess.Popen(command)

        logger.info("Процесс обработки очереди успешно запущен в фоне.")
        return {"status": "ok", "detail": "Processing started in background."}

    except Exception as e:
        logger.error(f"Ошибка при запуске дочернего процесса воркера: {e}", exc_info=True)
        return {"status": "error", "detail": str(e)}
