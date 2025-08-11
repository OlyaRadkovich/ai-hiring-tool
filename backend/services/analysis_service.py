from typing import List
import json
from backend.api.models import PreparationAnalysis, ResultsAnalysis, QuestionCategory, ScoreBreakdown
from backend.agents.pipeline_1_pre_interview import pipeline_config as pre_pipeline
from ..core.config import settings
from .mappers import parse_markdown_to_preparation_analysis
from pypdf import PdfReader
import io
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


class AnalysisService:
    """Service responsible for interview analysis business logic using AI Agents"""

    async def analyze_preparation(self, profile: str, file_content: bytes) -> PreparationAnalysis:
        """
        Analyze CV and candidate profile for interview preparation using the pre-interview pipeline.
        """
        api_key_to_use = settings.google_api_key
        if not api_key_to_use:
            raise ValueError("Google API key is not provided.")

        pipeline = pre_pipeline.create_pre_interview_pipeline(api_key_to_use)

        cv_text = ""
        file_obj = io.BytesIO(file_content)
        try:
            reader = PdfReader(file_obj)
            for page in reader.pages:
                cv_text += page.extract_text() or ""
        except Exception as e:
            cv_text = file_content.decode('utf-8', errors='ignore')

        message_for_agent = types.Content(
            role="user",
            parts=[
                types.Part(text=cv_text),
                types.Part(text=f"### Требования к вакансии\n{profile}")
            ]
        )

        session_service = InMemorySessionService()

        session_id = "preparation_session_123"
        user_id = "prep_user"
        session = await session_service.create_session(app_name=settings.app_name, user_id=user_id,
                                                       session_id=session_id)

        runner = Runner(agent=pipeline, app_name=settings.app_name, session_service=session_service)

        pipeline_result_markdown = ""

        async for event in runner.run_async(session_id="preparation_session_123", user_id="prep_user",
                                new_message=message_for_agent):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        pipeline_result_markdown += part.text + " "


        return parse_markdown_to_preparation_analysis(pipeline_result_markdown.strip())

    async def analyze_results(self, video_link: str, matrix_content: bytes) -> ResultsAnalysis:
        """
        Analyze interview results using the post-interview pipeline.
        """
        api_key_to_use = settings.google_api_key
        if not api_key_to_use:
            raise ValueError("Google API key is not provided.")

        # 2. Здесь будет логика для второго пайплайна, который мы пока не создали.
        # Например:
        # pipeline = post_pipeline.create_post_interview_pipeline(api_key_to_use)
        # context = { 'video_link': video_link, 'matrix_content': matrix_content }
        # pipeline_result_text = await pipeline.run(context)

        # 3. Здесь будет логика маппинга результата от второго пайплайна
        # в объект ResultsAnalysis.

        return ResultsAnalysis(
            message="Interview analysis completed successfully",
            transcription="Transcribed text from video analysis.",
            scores=ScoreBreakdown(
                technical=90, communication=85, leadership=88, cultural=80, overall=85
            ),
            strengths=["...", "..."],
            concerns=["...", "..."],
            recommendation="RECOMMEND HIRE",
            reasoning="Reasoning for recommendation.",
            topicsDiscussed=["Topic 1", "Topic 2"]
        )
