from fastapi import APIRouter, UploadFile, File, Form, Depends
from backend.api.models import PreparationAnalysis
from backend.api.deps import get_analysis_service
from backend.services.analysis_service import AnalysisService
from backend.utils.validators import FileValidator

router = APIRouter()

@router.post("/analyze", response_model=PreparationAnalysis)
async def analyze_preparation(
    profile: str = Form(...),
    file: UploadFile = File(...),
    analysis_service: AnalysisService = Depends(get_analysis_service)
) -> PreparationAnalysis:
    """Analyze CV and profile for interview preparation"""
    # Validate file
    FileValidator.validate_cv_file(file)
    
    # Read file content
    file_content = await file.read()
    
    return await analysis_service.analyze_preparation(profile, file_content)


