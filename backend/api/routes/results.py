import uuid
import json
from multiprocessing import Queue
from typing import Optional
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException,
    status
)
from loguru import logger

from backend.queue.manager import get_task_queue, get_task_store
from backend.api.models import TaskResponse, ErrorResponse
from backend.utils.validators import FileValidator

router = APIRouter()


@router.post(
    "/",
    summary="Queue Interview Analysis Task",
    description="Accepts interview data, queues the analysis task, and returns immediately.",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=TaskResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    }
)
async def queue_analysis_task(
        video_link: str = Form(..., description="Link to the interview video recording"),
        competency_matrix_link: str = Form(..., description="Link to the competency matrix"),
        department_values_link: str = Form(..., description="Link to department values document"),
        employee_portrait_link: str = Form(..., description="Link to the employee portrait document"),
        job_requirements_link: str = Form(..., description="Link to the job requirements"),
        cv_file: Optional[UploadFile] = File(None, description="Candidate's CV file (optional)"),
        task_queue: Queue = Depends(get_task_queue),
        task_store: dict = Depends(get_task_store)
):
    """
    This endpoint receives all necessary data for analysis,
    creates a unique task, places it in the background queue,
    and returns the task ID.
    """
    if cv_file:
        FileValidator.validate_cv_file_results(cv_file)

    task_id = str(uuid.uuid4())
    cv_filename = cv_file.filename if cv_file else "No CV provided"
    logger.info(f"Received analysis request for CV: {cv_filename}. Assigned task ID: {task_id}")

    try:
        task_store[task_id] = {"status": "processing"}

        cv_content_bytes = await cv_file.read() if cv_file else None

        task_details = {
            "task_id": task_id,
            "cv_content_bytes": cv_content_bytes,
            "cv_filename": cv_filename,
            "video_link": video_link,
            "competency_matrix_link": competency_matrix_link,
            "department_values_link": department_values_link,
            "employee_portrait_link": employee_portrait_link,
            "job_requirements_link": job_requirements_link
        }

        task_queue.put(task_details)
        logger.info(f"Task {task_id} for {cv_filename} has been successfully queued.")

        return TaskResponse(
            message="Analysis task has been accepted for processing.",
            task_id=task_id
        )

    except Exception as e:
        logger.error(f"Failed to queue task {task_id}: {e}", exc_info=True)
        task_store[task_id] = {"status": "failed", "error": "Failed to queue the task."}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not queue the analysis task."
        )


@router.get(
    "/{task_id}/status",
    summary="Get Task Status",
    description="Poll this endpoint to get the status and result of a background task."
)
async def get_task_status(task_id: str, task_store: dict = Depends(get_task_store)):
    """
    Retrieves the status of a task from the shared task store.
    If the task is completed, it parses the JSON result before returning.
    """
    task_info = task_store.get(task_id)
    if not task_info:
        logger.warning(f"Status requested for non-existent task ID: {task_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

    current_status = task_info.get("status")
    logger.debug(f"Status checked for task {task_id}: {current_status}")

    if current_status == "completed":
        result_json_string = task_info.get("result_json")
        if result_json_string:
            parsed_result = json.loads(result_json_string)
            return {"status": "completed", "result": parsed_result}
        else:
            logger.error(f"Task {task_id} is completed but has no result_json.")
            return {"status": "failed", "error": "Completed task is missing result data."}

    elif current_status == "failed":
        return {"status": "failed", "error": task_info.get("error", "Unknown error")}

    else:
        return {"status": "processing"}