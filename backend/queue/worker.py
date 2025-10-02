import os
import time

from loguru import logger
from redis import from_url
from redis.exceptions import ConnectionError
from rq import Worker

listen = ["results_processing"]
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
conn = None

retry_interval = 5
max_retries = 12

for i in range(max_retries):
    try:
        conn = from_url(redis_url)
        conn.ping()
        logger.success("Успешное подключение к Redis!")
        break
    except ConnectionError as e:
        logger.warning(f"Не удалось подключиться к Redis: {e}. Попытка {i + 1} из {max_retries}...")
        if i == max_retries - 1:
            logger.error("Не удалось подключиться к Redis после нескольких попыток. Воркер останавливается.")
            exit(1)
        time.sleep(retry_interval)


if __name__ == '__main__':
    if conn:
        logger.info(f"Запускаю воркер RQ, который слушает очереди: {listen}")
        worker = Worker(
            queues=listen,
            connection=conn
        )
        worker.work(logging_level="INFO")
    else:
        logger.error("Соединение с Redis не установлено. Воркер не может быть запущен.")
