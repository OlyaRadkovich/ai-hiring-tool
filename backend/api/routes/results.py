import os
import httpx
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, status
from loguru import logger
from rq import Queue

from backend.api.deps import get_results_queue
from backend.api.models import ErrorResponse, JobStatusResponse
from backend.utils.validators import FileValidator

router = APIRouter()


@router.post(
    "/",
    response_model=JobStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Запустить анализ результатов интервью",
    description="Принимает данные для анализа, ставит задачу в очередь и немедленно возвращает ее ID."
)
async def create_analysis_task(
        cv_file: Optional[UploadFile] = File(None, description="Резюме кандидата (.pdf, .docx, .txt)."),
        video_link: str = Form(..., description="Ссылка на видеозапись собеседования."),
        competency_matrix_link: str = Form(..., description="Ссылка на матрицу компетенций QA/AQA."),
        department_values_link: str = Form(..., description="Ссылка на ценности департамента."),
        employee_portrait_link: str = Form(..., description="Ссылка на портрет сотрудника."),
        job_requirements_link: str = Form(..., description="Ссылка на требования к вакансии."),
        queue: Queue = Depends(get_results_queue)
):
    """
    Эндпоинт для постановки задачи анализа результатов интервью в очередь.
    """
    if cv_file:
        FileValidator.validate_cv_file_results(cv_file)

    cv_bytes: Optional[bytes] = await cv_file.read() if cv_file and cv_file.file else None
    cv_filename: Optional[str] = cv_file.filename if cv_file else None

    logger.info("Постановка задачи на анализ в очередь...")
    try:
        job = queue.enqueue(
            "backend.queue.tasks.run_analysis_pipeline",
            cv_bytes=cv_bytes,
            cv_filename=cv_filename,
            video_link=video_link,
            competency_matrix_link=competency_matrix_link,
            department_values_link=department_values_link,
            employee_portrait_link=employee_portrait_link,
            job_requirements_link=job_requirements_link,
            job_timeout="2h"
        )
        logger.info(f"Задача {job.id} добавлена в очередь.")

        try:
            worker_url = os.getenv("WORKER_URL")
            if worker_url:
                logger.info(f"Отправка 'пинка' воркеру по адресу: {worker_url}")

                async with httpx.AsyncClient() as client:
                    response = await client.post(f"{worker_url}/process", timeout=10.0)
                    logger.info(f"'Пинок' воркеру отправлен. Статус ответа воркера: {response.status_code}")
            else:
                logger.warning("Переменная окружения WORKER_URL не установлена. 'Пинок' не отправлен.")

        except Exception as e:
            logger.error(f"Не удалось отправить 'пинок' воркеру: {e}", exc_info=True)

        return JobStatusResponse(job_id=job.id, status=job.get_status())

    except Exception as e:
        logger.error(f"Не удалось поставить задачу в очередь: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось поставить задачу в очередь из-за внутренней ошибки."
        )


@router.get(
    "/status/{job_id}",
    response_model=JobStatusResponse,
    responses={
        404: {"model": ErrorResponse},
    },
    summary="Проверить статус задачи анализа",
    description="Возвращает текущий статус задачи и результат, если она успешно завершена."
)
def get_analysis_status(job_id: str, queue: Queue = Depends(get_results_queue)):
    """
    Проверяет статус задачи по ее ID.
    """
    logger.info(f"Проверка статуса для задачи {job_id}")
    job = queue.fetch_job(job_id)

    if job is None:
        logger.warning(f"Попытка проверить статус для несуществующей задачи с ID {job_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Задача с ID {job_id} не найдена.")

    job_status = job.get_status()
    logger.info(f"Проверка статуса для задачи {job_id}. Текущий статус: {job_status}")

    response_data = {"job_id": job.id, "status": job_status}

    if job_status == 'finished':
        logger.success(f"Задача {job_id} успешно завершена. Отправляем результат клиенту.")
        result = job.result
        if hasattr(result, 'model_dump'):
            response_data["result"] = result.model_dump()
        else:
            response_data["result"] = result

    elif job_status == 'failed':
        logger.error(f"Задача {job_id} провалена. Отправляем ошибку клиенту.")
        error_message = job.exc_info.strip().split('\n')[-1] if job.exc_info else "Неизвестная ошибка в воркере."
        response_data["error"] = error_message

    return JobStatusResponse(**response_data)
