from fastapi import APIRouter, UploadFile, File, Form, status, HTTPException, Depends
from loguru import logger
from backend.api.models import ResultsAnalysis, ErrorResponse
from backend.services.analysis_service import AnalysisService
from backend.api.deps import get_analysis_service
from googleapiclient.errors import HttpError
from fastapi.responses import StreamingResponse

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
    description="Принимает ссылку на видеоинтервью и матрицу компетенций для генерации фидбэка."
)
async def analyze_results_endpoint(
        video_link: str = Form(..., description="Link to the interview video."),
        matrix_file: UploadFile = File(..., description="Competency matrix file (.xlsx, .xls, .csv, .pdf)."),
        analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Анализирует видеоинтервью и матрицу компетенций для генерации фидбэка и оценок.
    """
    if not matrix_file.filename.lower().endswith(('.pdf', '.xls', '.xlsx', '.csv')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недопустимый тип файла для матрицы компетенций."
        )

    try:
        matrix_content_bytes = await matrix_file.read()

        analysis_result = await analysis_service.analyze_results(
            video_link=video_link,
            matrix_content=matrix_content_bytes
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
    except Exception as e:
        logger.error(f"Произошла непредвиденная ошибка: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Произошла внутренняя ошибка сервера: {str(e)}"
        )


@router.post(
    "/export",
    summary="Экспорт отчета в DOCX",
    description="Принимает JSON с результатами анализа и возвращает DOCX файл.",
    response_class=StreamingResponse
)
async def export_results_endpoint(
        results: ResultsAnalysis,
        analysis_service: AnalysisService = Depends(get_analysis_service)
):
    try:
        file_stream = analysis_service.create_docx_report(results)

        headers = {
            'Content-Disposition': 'attachment; filename="Interview_Report.docx"'
        }

        return StreamingResponse(
            file_stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers=headers
        )
    except Exception as e:
        logger.error(f"Ошибка при создании DOCX отчета: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Не удалось сгенерировать DOCX отчет: {str(e)}"
        )