from pydantic import BaseModel, Field
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

class CandidateInfo(BaseModel):
    full_name: str = Field(..., description="Полное имя и фамилия кандидата")
    experience_years: str = Field(..., description="Общее количество лет опыта")
    tech_stack: List[str] = Field(..., description="Список ключевых технологий")
    domains: List[str] = Field(..., description="Список доменных областей")
    tasks: List[str] = Field(..., description="Список задач, которые выполнял кандидат")

class LanguageProficiency(BaseModel):
    language: str = Field("English", description="Иностранный язык")
    level: str = Field(..., description="Уровень владения языком")
    assessment: str = Field(..., description="Краткая оценка уровня")

class InterviewAnalysis(BaseModel):
    topics: List[str] = Field(..., description="Темы, затронутые на собеседовании")
    tech_assessment: str = Field(..., description="Развернутая оценка технических знаний")
    comm_skills_assessment: str = Field(..., description="Оценка коммуникационных навыков")
    language_proficiency: LanguageProficiency

class FinalConclusion(BaseModel):
    recommendation: str = Field(..., description="Финальная рекомендация (например, 'Не рекомендуем')")
    assessed_level: str = Field(..., description="Оцененный уровень (например, 'Intern')")
    summary: str = Field(..., description="Развернутое финальное заключение")

class FullReport(BaseModel):
    ai_summary: str = Field(..., description="Краткое AI-саммари всего отчета")
    candidate_info: CandidateInfo
    interview_analysis: InterviewAnalysis
    team_fit_assessment: str = Field(..., description="Оценка соответствия команде")
    additional_info: List[str] = Field(..., description="Другие важные моменты")
    conclusion: FinalConclusion
    recommendations_for_candidate: List[str] = Field(..., description="Рекомендации для кандидата")

class ResultsAnalysis(BaseResponse):
    report: FullReport
