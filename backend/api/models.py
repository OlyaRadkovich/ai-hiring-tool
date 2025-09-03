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
    projects: List[str] = Field(..., description="Краткое описание проектов, в которых участвовал кандидат")
    domains: List[str] = Field(..., description="Список доменных областей")
    tasks: List[str] = Field(..., description="Список задач, которые выполнял кандидат")

class InterviewAnalysis(BaseModel):
    topics: List[str] = Field(..., description="Темы, затронутые на собеседовании")
    tech_assignment: str = Field(..., description="Информация о том, выдавалось ли техническое задание")
    knowledge_assessment: str = Field(..., description="Развернутая оценка знаний кандидата по затронутым темам")

class CommunicationSkills(BaseModel):
    assessment: str = Field(..., description="Оценка коммуникационных навыков и самопрезентации")

class ForeignLanguages(BaseModel):
    assessment: str = Field(..., description="Оценка уровня владения иностранными языками")

class FinalConclusion(BaseModel):
    recommendation: str = Field(..., description="Финальная рекомендация (например, 'Не рекомендуем для работы в штате')")
    assessed_level: str = Field(..., description="Оцененный уровень (например, 'Intern')")
    summary: str = Field(..., description="Развернутое финальное заключение из 1-2 предложений")

class FullReport(BaseModel):
    ai_summary: str = Field(..., description="Краткое AI-саммари всего отчета с финальной рекомендацией")
    candidate_info: CandidateInfo
    interview_analysis: InterviewAnalysis
    communication_skills: CommunicationSkills
    foreign_languages: ForeignLanguages
    team_fit: str = Field(..., description="Оценка соответствия кандидата команде, ее ценностям и взглядам")
    additional_information: List[str] = Field(..., description="Другие важные моменты и наблюдения")
    conclusion: FinalConclusion
    recommendations_for_candidate: List[str] = Field(..., description="Рекомендации по дальнейшему развитию кандидата")

class ResultsAnalysis(BaseResponse):
    report: FullReport
