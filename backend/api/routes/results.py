import io
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, status, HTTPException, Depends
from google.genai.errors import ServerError
from loguru import logger
from backend.api.models import ResultsAnalysis, ErrorResponse
from backend.services.analysis_service import AnalysisService
from backend.api.deps import get_analysis_service
from googleapiclient.errors import HttpError
from backend.utils.validators import FileValidator

router = APIRouter()


@router.post(
    "/",
    response_model=ResultsAnalysis,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Анализ результатов интервью",
    description="Принимает полный набор данных для генерации развернутого фидбэка по кандидату."
)
async def analyze_results_endpoint(
        cv_file: Optional[UploadFile] = File(None, description="Резюме кандидата (.pdf, .docx, .txt)."),
        video_link: str = Form(..., description="Ссылка на видеозапись собеседования."),
        competency_matrix_link: str = Form(..., description="Ссылка на матрицу компетенций QA/AQA."),
        department_values_link: str = Form(..., description="Ссылка на ценности департамента."),
        employee_portrait_link: str = Form(..., description="Ссылка на портрет сотрудника."),
        job_requirements_link: str = Form(..., description="Ссылка на требования к вакансии."),
        analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Эндпоинт для анализа результатов интервью.
    Принимает CV (опционально), ссылку на видео и ссылки на документы с требованиями.
    """
    try:

        if cv_file:
            FileValidator.validate_cv_file_results(cv_file)

        cv_file_content = io.BytesIO(cv_file.file.read()) if cv_file and cv_file.file else None

        analysis_result = await analysis_service.analyze_results(
            cv_file=cv_file_content,
            cv_filename=cv_file.filename if cv_file else None,
            video_link=video_link,
            competency_matrix_link=competency_matrix_link,
            department_values_link=department_values_link,
            employee_portrait_link=employee_portrait_link,
            job_requirements_link=job_requirements_link
        )
        return analysis_result

    except HttpError as he:
        sa_email = "не удалось определить"
        if analysis_service.drive_service:
            sa_email = analysis_service.drive_service.credentials.service_account_email

        logger.error(f"Получена ошибка Google API: Status={he.status_code}, Reason={he.reason}")

        detail_message = f"Ошибка Google API: {he.reason}. " \
                         f"Убедитесь, что вы предоставили доступ к файлу для сервисного аккаунта с email: {sa_email}"

        raise HTTPException(
            status_code=he.status_code or 400,
            detail=detail_message
        )
    except ValueError as ve:
        logger.error(f"Ошибка значения в пайплайне: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except ServerError as e:
        logger.warning(f"Сервер Google перегружен: {e.message}. Попробуйте позже.")
        raise HTTPException(
            status_code=503,
            detail="AI-модель временно перегружена. Пожалуйста, повторите попытку через несколько минут."
        )
    except Exception as e:
        logger.error(f"Произошла непредвиденная ошибка: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Произошла внутренняя ошибка сервера: {e}"
        )
