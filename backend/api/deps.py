from backend.services.analysis_service import AnalysisService

# Lazy service instances
_analysis_service = None

def get_analysis_service() -> AnalysisService:
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisService()
    return _analysis_service


