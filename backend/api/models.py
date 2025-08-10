from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Base response models
class BaseResponse(BaseModel):
    message: str
    success: bool = True

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None

# Auth models
class UserInfo(BaseModel):
    email: str
    firstName: Optional[str] = None

class AuthResponse(BaseResponse):
    token: Optional[str] = None
    user: Optional[UserInfo] = None

# Analysis models
class QuestionCategory(BaseModel):
    category: str
    questions: List[str]

class PreparationAnalysis(BaseResponse):
    keyTopics: List[str]
    suggestedQuestions: List[QuestionCategory]

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
