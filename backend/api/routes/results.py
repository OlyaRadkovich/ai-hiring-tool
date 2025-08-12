# -*- coding: utf-8 -*-

from fastapi import APIRouter, UploadFile, File, Form, status, HTTPException
from typing import Optional
from backend.api.models import ResultsAnalysis, ErrorResponse
from backend.services.analysis_service import AnalysisService

router = APIRouter()
analysis_service = AnalysisService()


@router.post(
    "/",
    response_model=ResultsAnalysis,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Анализ результатов интервью",
    description="Принимает ссылку на видеоинтервью и матрицу компетенций для генерации фидбэка."
)
async def analyze_results_endpoint(
        video_link: str = Form(..., description="Link to the interview video."),
        matrix_file: UploadFile = File(..., description="Competency matrix file (.xlsx, .xls, .csv, .pdf)."),
):
    """
    Анализирует видеоинтервью и матрицу компетенций для генерации фидбэка и оценок.
    """
    if not matrix_file.filename.lower().endswith(('.pdf', '.xls', '.xlsx', '.csv')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недопустимый тип файла для матрицы компетенций. Принимаются форматы .xlsx, .xls, .csv или .pdf"
        )

    try:
        matrix_content_bytes = await matrix_file.read()

        analysis_result = await analysis_service.analyze_results(
            video_link=video_link,
            matrix_content=matrix_content_bytes
        )
        return analysis_result

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Произошла ошибка при анализе результатов: {str(e)}"
        )
