import os
from fastapi import FastAPI, status
from loguru import logger
from redis import from_url
from rq import Worker

app = FastAPI(
    title="AI Hiring Tool - On-Demand Worker",
    description="HTTP-Redis worker",
    version="1.0.0"
)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
conn = from_url(REDIS_URL)

LISTEN_QUEUES = ["results", "processing"]


@app.post("/process", status_code=status.HTTP_202_ACCEPTED)
async def trigger_processing():
    logger.info("Received processing trigger")
    if not conn:
        logger.error("Redis connection is not available")
        return {"status": "error", "detail": "Redis connection not available"}

    try:
        worker = Worker(queues=LISTEN_QUEUES, connection=conn)
        did_process_anything = worker.work(burst=True)
        logger.info(f"Worker processed queue: {did_process_anything}")
        return {"status": "ok", "processed": did_process_anything}
    except Exception as e:
        logger.error(f"Error processing queue: {e}", exc_info=True)
        return {"status": "error", "detail": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
