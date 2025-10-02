# backend/worker_main.py
from fastapi import FastAPI, status
from loguru import logger
from redis import from_url
from rq import Worker
import os

app = FastAPI()
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
conn = from_url(redis_url)


@app.post("/process", status_code=status.HTTP_202_ACCEPTED)
def trigger_processing():
    """
    Этот эндпоинт принимает 'пинок' и запускает обработку очереди.
    """
    logger.info("Получен 'пинок', запускаю обработку очереди...")
    try:
        listen = ["results_processing"]
        worker = Worker(queues=listen, connection=conn)
        worker.work(burst=True)

        logger.info("Обработка очереди завершена.")
        return {"message": "Queue processing triggered and completed."}
    except Exception as e:
        logger.error(f"Ошибка при обработке очереди: {e}")
        return {"message": f"Error during queue processing: {e}"}
