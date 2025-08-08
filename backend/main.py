from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user: Dict[str, Any]


class PreparationResponse(BaseModel):
    keyTopics: List[str]
    suggestedQuestions: List[Dict[str, Any]]


class Scores(BaseModel):
    technical: int
    communication: int
    leadership: int
    cultural: int
    overall: int


class ResultsResponse(BaseModel):
    transcription: str
    scores: Scores
    strengths: List[str]
    concerns: List[str]
    recommendation: str
    reasoning: str
    topicsDiscussed: List[str]


app = FastAPI(title="InterviewAI Backend", openapi_url="/api/openapi.json")

origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    # В реальном проекте здесь должна быть проверка пользователя и выдача JWT
    return LoginResponse(
        token="dummy-token",
        user={
            "email": payload.email,
            "name": "John Doe",
        },
    )


@app.post("/api/auth/register", response_model=LoginResponse)
def register(payload: LoginRequest) -> LoginResponse:
    # Заглушка регистрации: возвращаем такой же ответ, как и логин
    return LoginResponse(
        token="dummy-token",
        user={
            "email": payload.email,
            "name": "John Doe",
        },
    )


@app.post("/api/prep/analyze", response_model=PreparationResponse)
async def analyze_preparation(
    profile: str = Form(...),
    file: UploadFile = File(...),
) -> PreparationResponse:
    # В проде тут будет разбор файла и генерация подсказок (LLM)
    return PreparationResponse(
        keyTopics=[
            "React and TypeScript expertise",
            "Frontend architecture patterns",
            "State management solutions",
            "Performance optimization",
            "Team leadership experience",
        ],
        suggestedQuestions=[
            {
                "category": "Technical Skills",
                "questions": [
                    "Can you walk me through your experience with React hooks and state management?",
                    "How do you approach performance optimization in React applications?",
                    "Describe a challenging TypeScript implementation you've worked on.",
                ],
            },
            {
                "category": "Architecture & Design",
                "questions": [
                    "How do you structure large-scale frontend applications?",
                    "What's your experience with micro-frontend architectures?",
                    "How do you ensure code maintainability across teams?",
                ],
            },
            {
                "category": "Leadership & Collaboration",
                "questions": [
                    "Describe your experience mentoring junior developers.",
                    "How do you handle technical disagreements within the team?",
                    "What's your approach to code reviews and knowledge sharing?",
                ],
            },
        ],
    )


@app.post("/api/results/analyze", response_model=ResultsResponse)
async def analyze_results(
    video_link: str = Form(...),
    matrix: UploadFile = File(...),
) -> ResultsResponse:
    # В проде: скачивание видео, транскрипция, анализ по матрице компетенций
    return ResultsResponse(
        transcription=(
            "The candidate demonstrated strong technical knowledge when discussing React hooks and state "
            "management. They provided specific examples of performance optimization techniques including "
            "code splitting and lazy loading. When asked about team leadership, they shared their experience "
            "mentoring 3 junior developers and implementing code review processes. The candidate showed enthusiasm "
            "for learning new technologies and expressed interest in contributing to architectural decisions."
        ),
        scores=Scores(
            technical=85,
            communication=78,
            leadership=82,
            cultural=75,
            overall=80,
        ),
        strengths=[
            "Strong technical expertise in React and TypeScript",
            "Clear communication style with concrete examples",
            "Proven leadership experience with junior developers",
            "Proactive approach to code quality and best practices",
        ],
        concerns=[
            "Limited experience with large-scale system architecture",
            "Could benefit from more exposure to cross-functional collaboration",
            "Might need support transitioning to senior leadership role",
        ],
        recommendation="RECOMMEND HIRE",
        reasoning=(
            "Candidate demonstrates strong technical skills and leadership potential. While there are areas "
            "for growth, their foundation is solid and they show clear enthusiasm for learning. Recommend proceeding "
            "to final round with focus on architecture discussions."
        ),
        topicsDiscussed=[
            "React Hooks & State Management",
            "Performance Optimization",
            "Code Review Processes",
            "Team Mentoring",
            "Testing Strategies",
            "CI/CD Implementation",
        ],
    )


