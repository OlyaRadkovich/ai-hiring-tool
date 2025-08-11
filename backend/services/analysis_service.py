import os
import json
import io
from loguru import logger

# Модели Pydantic и конфиг
from backend.api.models import PreparationAnalysis, ResultsAnalysis, ScoreBreakdown
from ..core.config import settings

# Импортируем агентов
from backend.agents.pipeline_1_pre_interview.agent_1_data_parser import agent_1_data_parser
from backend.agents.pipeline_1_pre_interview.agent_2_profiler import agent_2_profiler
from backend.agents.pipeline_1_pre_interview.agent_3_plan_generator import agent_3_plan_generator

# Утилиты
from pypdf import PdfReader
import docx
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


class AnalysisService:
    """Service responsible for interview analysis business logic using AI Agents"""

    async def analyze_preparation(self, profile: str, cv_file: io.BytesIO, filename: str) -> PreparationAnalysis:
        logger.info("Начало процесса подготовки к интервью...")

        api_key_to_use = settings.google_api_key
        if not api_key_to_use:
            logger.error("Google API key не предоставлен.")
            raise ValueError("Google API key is not provided.")

        # --- ⭐️ КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: Устанавливаем API ключ как переменную окружения ---
        os.environ['GOOGLE_API_KEY'] = api_key_to_use
        logger.success("API ключ Google установлен как переменная окружения.")

        # --- Шаг 1: Извлечение текста из файла ---
        logger.info(f"Извлечение текста из файла: {filename}")
        cv_text = ""
        try:
            if filename.lower().endswith('.pdf'):
                reader = PdfReader(cv_file)
                cv_text = "\n".join(page.extract_text() or "" for page in reader.pages)
                logger.success("Текст из PDF успешно извлечен.")
            elif filename.lower().endswith('.docx'):
                doc = docx.Document(cv_file)
                lines = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
                cv_text = "\n".join(lines)
                logger.success("Текст из DOCX успешно извлечен и очищен.")
            else:
                cv_text = cv_file.read().decode('utf-8', errors='ignore')
                logger.success("Файл прочитан как текстовый.")
        except Exception as e:
            logger.error(f"Ошибка при чтении файла {filename}: {e}")
            raise ValueError(f"Could not process file: {filename}")

        logger.debug(f"Извлеченный текст резюме (первые 200 символов): {cv_text[:200]}...")

        # --- Настройка сессии ---
        session_service = InMemorySessionService()
        session_id = "preparation_session_123"
        user_id = "prep_user"
        await session_service.create_session(app_name=settings.app_name, user_id=user_id, session_id=session_id)

        # --- Запуск Агента 1 ---
        logger.info("🚀 Запуск agent_1_data_parser...")
        runner_1 = Runner(agent=agent_1_data_parser, app_name=settings.app_name, session_service=session_service)
        message_for_agent_1 = types.Content(role="user", parts=[types.Part(text=cv_text), types.Part(
            text=f"### Требования к вакансии\n{profile}")])
        agent_1_output = ""
        async for event in runner_1.run_async(session_id=session_id, user_id=user_id,
                                              new_message=message_for_agent_1):  # Ключ больше не передается здесь
            if event.content and event.content.parts:
                agent_1_output += "".join(part.text for part in event.content.parts if part.text)

        logger.success("✅ agent_1_data_parser завершил работу.")
        logger.debug(f"Выходные данные Агента 1 (JSON):\n{agent_1_output}")

        # --- Запуск Агента 2 ---
        logger.info("🚀 Запуск agent_2_profiler...")
        runner_2 = Runner(agent=agent_2_profiler, app_name=settings.app_name, session_service=session_service)
        message_for_agent_2 = types.Content(role="user", parts=[types.Part(text=agent_1_output)])
        agent_2_output = ""
        async for event in runner_2.run_async(session_id=session_id, user_id=user_id, new_message=message_for_agent_2):
            if event.content and event.content.parts:
                agent_2_output += "".join(part.text for part in event.content.parts if part.text)

        logger.success("✅ agent_2_profiler завершил работу.")
        logger.debug(f"Выходные данные Агента 2 (Текстовый профиль):\n{agent_2_output}")

        # --- Запуск Агента 3 ---
        logger.info("🚀 Запуск agent_3_plan_generator...")
        runner_3 = Runner(agent=agent_3_plan_generator, app_name=settings.app_name, session_service=session_service)
        message_for_agent_3 = types.Content(role="user", parts=[types.Part(text=agent_2_output)])
        final_output = ""
        async for event in runner_3.run_async(session_id=session_id, user_id=user_id, new_message=message_for_agent_3):
            if event.content and event.content.parts:
                final_output += "".join(part.text for part in event.content.parts if part.text)

        logger.success("✅ agent_3_plan_generator завершил работу.")
        logger.debug(f"Финальные выходные данные от Агента 3:\n{final_output}")

        # --- Финальный парсинг и возврат результата ---
        logger.info("Парсинг финального вывода в объект Pydantic...")
        try:
            # Убираем возможные ```json ``` обертки, если агент их вернет
            clean_json_str = final_output.strip().replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json_str)

            # Добавляем стандартное сообщение в ответ
            data["message"] = "Interview preparation plan created successfully."

            result = PreparationAnalysis(**data)
            logger.success("Процесс подготовки к интервью успешно завершен.")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON от Агента 3: {e}")
            logger.error(f"Полученный текст: {final_output}")
            raise ValueError("AI-сервис вернул некорректный формат данных.")

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
