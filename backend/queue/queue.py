import os
from redis import Redis
from rq import Queue

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

redis_conn = Redis.from_url(redis_url)
results_queue = Queue("results_processing", connection=redis_conn)
