import asyncio
import io
from typing import Optional

from loguru import logger

from backend.services.analysis_service import AnalysisService


def run_analysis_pipeline(
        cv_bytes: Optional[bytes],
        cv_filename: Optional[str],
        video_link: str,
        competency_matrix_link: str,
        department_values_link: str,
        employee_portrait_link: str,
        job_requirements_link: str
):
    """
    Эта функция будет выполняться воркером RQ.
    Она создает сервис анализа и запускает пайплайн обработки результатов.
    """
    logger.info("Воркер получил новую задачу на анализ результатов интервью.")

    try:
        service = AnalysisService()
        cv_file = io.BytesIO(cv_bytes) if cv_bytes else None

        result = asyncio.run(service.analyze_results(
            cv_file=cv_file,
            cv_filename=cv_filename,
            video_link=video_link,
            competency_matrix_link=competency_matrix_link,
            department_values_link=department_values_link,
            employee_portrait_link=employee_portrait_link,
            job_requirements_link=job_requirements_link
        ))

        logger.success(f"Анализ успешно завершен. Результат: {result.message}")

        return result.model_dump()

    except Exception as e:
        logger.error(f"Ошибка при выполнении задачи анализа: {e}", exc_info=True)
        raise
