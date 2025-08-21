from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class BaseResponse(BaseModel):
    message: str
    success: bool = True

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None

class MatchingItem(BaseModel):
    criterion: str
    match: str
    comment: str

class Conclusion(BaseModel):
    summary: str
    recommendations: str
    interview_topics: List[str]
    values_assessment: str

class Report(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    matching_table: List[MatchingItem]
    candidate_profile: str
    conclusion: Conclusion

class PreparationAnalysis(BaseResponse):
    report: Report

class ScoreBreakdown(BaseModel):
    technical: int
    communication: int
    leadership: int
    cultural: int
    overall: int

class ResultsAnalysis(BaseResponse):
    transcription: str
    scores: ScoreBreakdown
    strengths: List[str]
    concerns: List[str]
    recommendation: str
    reasoning: str
    topicsDiscussed: List[str]
