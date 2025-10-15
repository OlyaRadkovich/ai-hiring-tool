import os

from redis import from_url
from rq import Queue

from backend.services.analysis_service import AnalysisService


def get_analysis_service() -> AnalysisService:
    return AnalysisService()


redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
redis_conn = from_url(redis_url)
results_queue = Queue("results_processing", connection=redis_conn)


def get_results_queue() -> Queue:
    """FastAPI Dependency to get the RQ queue instance."""
    return results_queue
