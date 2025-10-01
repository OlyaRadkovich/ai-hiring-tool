import logging
import asyncio
import io
import json
from multiprocessing import Queue
from backend.services.analysis_service import AnalysisService
from backend.queue.manager import get_task_store

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_analysis_task(task_details: dict):
    """
    Runs the actual analysis task and updates its status in the task store.
    """
    task_store = get_task_store()
    task_id = task_details.get("task_id")
    cv_filename = task_details.get("cv_filename")

    logger.info(f"WORKER-SIDE: Starting processing for task {task_id} (CV: {cv_filename})...")

    try:
        cv_content_bytes = task_details.get("cv_content_bytes")
        cv_file_like_object = io.BytesIO(cv_content_bytes)
        video_link = task_details.get("video_link")
        competency_matrix_link = task_details.get("competency_matrix_link")
        department_values_link = task_details.get("department_values_link")
        employee_portrait_link = task_details.get("employee_portrait_link")
        job_requirements_link = task_details.get("job_requirements_link")

        analysis_service = AnalysisService()

        result_model = asyncio.run(analysis_service.analyze_results(
            cv_file=cv_file_like_object,
            cv_filename=cv_filename,
            video_link=video_link,
            competency_matrix_link=competency_matrix_link,
            department_values_link=department_values_link,
            employee_portrait_link=employee_portrait_link,
            job_requirements_link=job_requirements_link
        ))

        logger.info(f"WORKER-SIDE: Analysis logic for task {task_id} completed successfully.")

        result_json_string = result_model.model_dump_json()
        logger.debug(f"WORKER-SIDE: Result for task {task_id} serialized to JSON string.")

        update_payload = {"status": "completed", "result_json": result_json_string}

        try:
            logger.info(f"WORKER-SIDE: Attempting to update task store for task {task_id}...")
            task_store[task_id] = update_payload
            logger.info(f"WORKER-SIDE: SUCCESSFULLY updated task store for task {task_id}.")
        except Exception as store_e:
            logger.critical(f"WORKER-SIDE: CRITICAL FAILURE updating task store for {task_id}: {store_e}",
                            exc_info=True)

    except Exception as e:
        logger.error(f"WORKER-SIDE: An error occurred in the main try block for task {task_id}: {e}", exc_info=True)
        try:
            task_store[task_id] = {"status": "failed", "error": str(e)}
            logger.info(f"WORKER-SIDE: Successfully marked task {task_id} as FAILED in task store.")
        except Exception as store_fail_e:
            logger.critical(f"WORKER-SIDE: CRITICAL FAILURE to even mark task {task_id} as FAILED: {store_fail_e}",
                            exc_info=True)


def worker(task_queue: Queue):
    """
    The main worker function that listens to the task queue indefinitely.
    """
    logger.info("WORKER-SIDE: Worker process started and ready for tasks...")
    while True:
        try:
            task_details = task_queue.get()
            if task_details is None:
                logger.info("WORKER-SIDE: Received shutdown signal. Worker is stopping.")
                break

            if isinstance(task_details, dict):
                run_analysis_task(task_details)
            else:
                logger.warning(f"WORKER-SIDE: Received a task of unknown format: {task_details}")

        except Exception as e:
            logger.critical(f"WORKER-SIDE: A critical error occurred in the worker loop: {e}", exc_info=True)