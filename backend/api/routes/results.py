from fastapi import APIRouter, UploadFile, File, Form


router = APIRouter(tags=["results"], prefix="/results")


@router.post("/analyze")
async def analyze_results(
    video_link: str = Form(...),
    matrix: UploadFile = File(...),
) -> dict:
    return {
        "transcription": (
            "The candidate demonstrated strong technical knowledge when discussing React hooks and state "
            "management. They provided specific examples of performance optimization techniques including "
            "code splitting and lazy loading. When asked about team leadership, they shared their experience "
            "mentoring 3 junior developers and implementing code review processes. The candidate showed enthusiasm "
            "for learning new technologies and expressed interest in contributing to architectural decisions."
        ),
        "scores": {
            "technical": 85,
            "communication": 78,
            "leadership": 82,
            "cultural": 75,
            "overall": 80,
        },
        "strengths": [
            "Strong technical expertise in React and TypeScript",
            "Clear communication style with concrete examples",
            "Proven leadership experience with junior developers",
            "Proactive approach to code quality and best practices",
        ],
        "concerns": [
            "Limited experience with large-scale system architecture",
            "Could benefit from more exposure to cross-functional collaboration",
            "Might need support transitioning to senior leadership role",
        ],
        "recommendation": "RECOMMEND HIRE",
        "reasoning": (
            "Candidate demonstrates strong technical skills and leadership potential. While there are areas "
            "for growth, their foundation is solid and they show clear enthusiasm for learning. Recommend proceeding "
            "to final round with focus on architecture discussions."
        ),
        "topicsDiscussed": [
            "React Hooks & State Management",
            "Performance Optimization",
            "Code Review Processes",
            "Team Mentoring",
            "Testing Strategies",
            "CI/CD Implementation",
        ],
    }


