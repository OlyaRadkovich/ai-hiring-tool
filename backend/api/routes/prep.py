from fastapi import APIRouter, UploadFile, File, Form


router = APIRouter(tags=["preparation"], prefix="/prep")


@router.post("/analyze")
async def analyze_preparation(
    profile: str = Form(...),
    file: UploadFile = File(...),
) -> dict:
    return {
        "keyTopics": [
            "React and TypeScript expertise",
            "Frontend architecture patterns",
            "State management solutions",
            "Performance optimization",
            "Team leadership experience",
        ],
        "suggestedQuestions": [
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
    }


