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
    summary="Анализ CV и профиля кандидата для подготовки к интервью",
    description="Принимает резюме и требования/фидбэк для генерации плана подготовки к собеседованию."
)
async def analyze_preparation_endpoint(
        profile: str = Form(..., description="Job requirements and recruiter feedback text."),
        cv_file: UploadFile = File(..., description="Candidate's CV in text, PDF, or DOCX format."),
        analysis_service: AnalysisService = Depends(get_analysis_service)
):
    if not cv_file.filename.lower().endswith(('.txt', '.pdf', '.docx')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недопустимый тип файла. Принимаются только .txt, .pdf или .docx."
        )

    try:
        logger.info("Received a new analysis request for interview preparation.")

        file_content_bytes = await cv_file.read()
        file_like_object = io.BytesIO(file_content_bytes)

        analysis_result = await analysis_service.analyze_preparation(
            profile=profile,
            cv_file=file_like_object,
            filename=cv_file.filename
        )

        logger.info("Analysis completed successfully. Returning result.")
        return analysis_result

    except ValueError as ve:
        logger.error(f"An error occurred: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"An error occurred during analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Произошла ошибка при анализе: {str(e)}"
        )