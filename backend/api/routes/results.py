from fastapi import APIRouter, UploadFile, File, Form, Depends
from backend.api.models import ResultsAnalysis
from backend.api.deps import get_analysis_service
from backend.services.analysis_service import AnalysisService
from backend.utils.validators import FileValidator

router = APIRouter()

@router.post("/analyze", response_model=ResultsAnalysis)
async def analyze_results(
    video_link: str = Form(...),
    matrix: UploadFile = File(...),
    analysis_service: AnalysisService = Depends(get_analysis_service)
) -> ResultsAnalysis:
    """Analyze interview results"""
    # Validate file
    FileValidator.validate_matrix_file(matrix)
    
    # Read file content
    matrix_content = await matrix.read()
    
    return await analysis_service.analyze_results(video_link, matrix_content)


