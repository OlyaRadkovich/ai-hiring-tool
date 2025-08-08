from typing import Generator
from backend.services.auth_service import AuthService
from backend.services.analysis_service import AnalysisService

# Lazy service instances
_auth_service = None
_analysis_service = None

def get_auth_service() -> AuthService:
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service

def get_analysis_service() -> AnalysisService:
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisService()
    return _analysis_service


