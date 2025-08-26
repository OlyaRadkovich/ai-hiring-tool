from fastapi import APIRouter, UploadFile, File, Form, status, HTTPException, Depends
from typing import Optional
from loguru import logger
import io
from backend.api.models import PreparationAnalysis, ErrorResponse
from backend.services.analysis_service import AnalysisService
from backend.api.deps import get_analysis_service

router = APIRouter()


@router.post(
    "/",
    response_model=PreparationAnalysis,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Анализ данных кандидата для подготовки к интервью",
    description="Принимает резюме, фидбэк и ссылку на требования для генерации плана интервью."
)
async def analyze_preparation_endpoint(
        cv_file: UploadFile = File(..., description="Резюме кандидата (.txt, .pdf, .docx)."),
        feedback_file: UploadFile = File(..., description="Фидбэк от рекрутера (.txt, .pdf, .docx)."),
        requirements_link: str = Form(..., description="Ссылка на Google Таблицу с требованиями."),
        analysis_service: AnalysisService = Depends(get_analysis_service)
):
    allowed_extensions = ('.txt', '.pdf', '.docx')
    if not cv_file.filename or not cv_file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый тип файла для резюме: {cv_file.filename}. Разрешены: .txt, .pdf, .docx."
        )
    if not feedback_file.filename or not feedback_file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый тип файла для фидбэка: {feedback_file.filename}. Разрешены: .txt, .pdf, .docx."
        )

    try:
        logger.info("Получен новый запрос на анализ для подготовки к интервью.")

        cv_content_bytes = await cv_file.read()
        cv_file_like_object = io.BytesIO(cv_content_bytes)

        feedback_content_bytes = await feedback_file.read()
        feedback_file_like_object = io.BytesIO(feedback_content_bytes)

        analysis_result = await analysis_service.analyze_preparation(
            cv_file=cv_file_like_object,
            cv_filename=cv_file.filename,
            feedback_file=feedback_file_like_object,
            feedback_filename=feedback_file.filename,
            requirements_link=requirements_link
        )

        logger.info("Анализ успешно завершен. Возвращается результат.")
        return analysis_result

    except ValueError as ve:
        logger.error(f"Ошибка значения в процессе анализа: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except IOError as ioe:
        logger.error(f"Ошибка ввода-вывода, возможно, проблема с Google Drive: {ioe}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ioe)
        )
    except Exception as e:
        logger.error(f"Произошла непредвиденная ошибка во время анализа: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Произошла внутренняя ошибка сервера: {str(e)}"
        )
