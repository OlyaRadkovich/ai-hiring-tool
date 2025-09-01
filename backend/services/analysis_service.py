import os
import json
import io
import asyncio
from loguru import logger

from backend.api.models import PreparationAnalysis, ResultsAnalysis, FullReport
from ..core.config import settings
from backend.utils import file_processing as fp
from backend.agents.pipeline_1_pre_interview.agent_1_data_parser import agent_1_data_parser
from backend.agents.pipeline_1_pre_interview.agent_2_grader import agent_2_grader
from backend.agents.pipeline_1_pre_interview.agent_3_report_generator import agent_3_report_generator
from backend.agents.pipeline_2_post_interview.agent_4_topic_extractor import agent_4_topic_extractor
from backend.agents.pipeline_2_post_interview.agent_5_final_report_generator import agent_5_final_report_generator

import assemblyai as aai
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.oauth2 import service_account
from googleapiclient.discovery import build


class AnalysisService:
    """Service responsible for interview analysis business logic using AI Agents"""

    def __init__(self):
        if settings.assemblyai_api_key:
            aai.settings.api_key = settings.assemblyai_api_key
            logger.success("Клиент AssemblyAI сконфигурирован.")
        else:
            logger.warning("API ключ для AssemblyAI не настроен в .env файле!")

        self.drive_service = None
        try:
            credentials_path = settings.google_application_credentials
            if os.path.exists(credentials_path):
                credentials = service_account.Credentials.from_service_account_file(credentials_path)
                self.drive_service = build('drive', 'v3', credentials=credentials)
                logger.success("Клиент Google Drive API успешно инициализирован.")
            else:
                logger.error(f"Файл учетных данных Google не найден по пути: {credentials_path}")
        except Exception as e:
            logger.error(f"Ошибка инициализации клиента Google Drive API: {e}")

    def _set_google_api_key(self):
        """
        Устанавливает ключ Google API как переменную окружения.
        """
        api_key_to_use = settings.google_api_key
        if not api_key_to_use:
            logger.error("Ключ Google API (google_api_key) не найден в .env файле.")
            raise ValueError("Google API key is not provided.")
        os.environ['GOOGLE_API_KEY'] = api_key_to_use
        logger.info("Ключ Google API установлен как переменная окружения для текущего запроса.")

    async def analyze_preparation(
            self,
            cv_file: io.BytesIO,
            cv_filename: str,
            feedback_text: str,
            requirements_link: str
    ) -> PreparationAnalysis:
        logger.info("Начало процесса оценки кандидата (Пайплайн 1)...")

        self._set_google_api_key()

        cv_text = fp.read_file_content(cv_file, cv_filename)

        requirements_file_id = fp.get_google_drive_file_id(requirements_link)
        requirements_text = await fp.download_sheet_from_drive(self.drive_service, requirements_file_id)

        session_service = InMemorySessionService()
        session_id = f"prep_session_{os.urandom(8).hex()}"
        user_id = "prep_user"
        await session_service.create_session(app_name=settings.app_name, user_id=user_id, session_id=session_id)

        logger.info("🚀 Запуск agent_1_data_parser...")
        runner_1 = Runner(agent=agent_1_data_parser, app_name=settings.app_name, session_service=session_service)
        message_for_agent_1 = types.Content(
            role="user",
            parts=[
                types.Part(text=f"cv_text: {cv_text}"),
                types.Part(text=f"requirements_text: {requirements_text}"),
                types.Part(text=f"feedback_text: {feedback_text}")
            ]
        )
        agent_1_output = ""
        async for event in runner_1.run_async(session_id=session_id, user_id=user_id, new_message=message_for_agent_1):
            if event.content and event.content.parts:
                agent_1_output += "".join(part.text for part in event.content.parts if part.text)

        logger.info("🚀 Запуск agent_2_grader...")
        runner_2 = Runner(agent=agent_2_grader, app_name=settings.app_name, session_service=session_service)
        message_for_agent_2 = types.Content(role="user", parts=[types.Part(text=agent_1_output)])
        agent_2_output = ""
        async for event in runner_2.run_async(session_id=session_id, user_id=user_id, new_message=message_for_agent_2):
            if event.content and event.content.parts:
                agent_2_output += "".join(part.text for part in event.content.parts if part.text)

        logger.info("🚀 Запуск agent_3_report_generator...")
        runner_3 = Runner(agent=agent_3_report_generator, app_name=settings.app_name, session_service=session_service)
        message_for_agent_3 = types.Content(role="user", parts=[types.Part(text=agent_2_output)])
        final_output = ""
        async for event in runner_3.run_async(session_id=session_id, user_id=user_id, new_message=message_for_agent_3):
            if event.content and event.content.parts:
                final_output += "".join(part.text for part in event.content.parts if part.text)

        logger.info("Парсинг финального вывода...")
        try:
            clean_json_str = final_output.strip().replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json_str)

            final_response_data = {
                "message": "Interview preparation report created successfully.",
                **data
            }
            return PreparationAnalysis(**final_response_data)
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON от Агента 3: {e}\nПолученный текст: {final_output}")
            raise ValueError("AI-сервис вернул некорректный формат данных.")
        except Exception as e:
            logger.error(f"Ошибка валидации Pydantic или другая ошибка: {e}")
            raise ValueError(f"Ошибка при формировании итогового ответа: {e}")

    async def analyze_results(
            self,
            cv_file: io.BytesIO,
            cv_filename: str,
            video_link: str,
            competency_matrix_link: str,
            department_values_link: str,
            employee_portrait_link: str,
            job_requirements_link: str
    ) -> ResultsAnalysis:
        logger.info("🚀 Запуск Пайплайна 2: Анализ результатов интервью...")
        self._set_google_api_key()

        video_file_id = fp.get_google_drive_file_id(video_link)

        async def transcribe_and_read():
            audio_stream = await fp.download_audio_from_drive(self.drive_service, video_file_id)
            transcription = await fp.transcribe_audio_assemblyai(audio_stream)
            if not transcription:
                raise ValueError("Транскрипция не вернула текст. Видео может быть без звука или слишком коротким.")
            cv_text = fp.read_file_content(cv_file, cv_filename)
            return transcription, cv_text

        async def download_drive_data():
            tasks = [
                fp.download_sheet_from_drive(self.drive_service, fp.get_google_drive_file_id(competency_matrix_link)),
                fp.download_sheet_from_drive(self.drive_service, fp.get_google_drive_file_id(department_values_link)),
                fp.download_sheet_from_drive(self.drive_service, fp.get_google_drive_file_id(employee_portrait_link)),
                fp.download_sheet_from_drive(self.drive_service, fp.get_google_drive_file_id(job_requirements_link)),
            ]
            return await asyncio.gather(*tasks)

        (transcription_text, cv_text), (matrix_text, values_text, portrait_text,
                                        requirements_text) = await asyncio.gather(
            transcribe_and_read(),
            download_drive_data()
        )

        session_service = InMemorySessionService()
        session_id = f"results_session_{os.urandom(8).hex()}"
        user_id = "results_user"
        await session_service.create_session(app_name=settings.app_name, user_id=user_id, session_id=session_id)

        logger.info("🚀 Запуск agent_4_topic_extractor...")
        runner_4 = Runner(agent=agent_4_topic_extractor, app_name=settings.app_name, session_service=session_service)
        message_for_agent_4 = types.Content(role="user", parts=[types.Part(text=transcription_text)])
        agent_4_output = ""
        async for event in runner_4.run_async(session_id=session_id, user_id=user_id, new_message=message_for_agent_4):
            if event.content and event.content.parts:
                agent_4_output += "".join(part.text for part in event.content.parts if part.text)

        combined_input_for_agent_5 = (
            f"### Транскрипция интервью:\n{transcription_text}\n\n"
            f"### CV кандидата:\n{cv_text}\n\n"
            f"### Требования к вакансии:\n{requirements_text}\n\n"
            f"### Матрица компетенций:\n{matrix_text}\n\n"
            f"### Ценности департамента:\n{values_text}\n\n"
            f"### Портрет идеального сотрудника:\n{portrait_text}"
        )

        logger.info("🚀 Запуск agent_5_final_report_generator...")
        runner_5 = Runner(agent=agent_5_final_report_generator, app_name=settings.app_name,
                          session_service=session_service)
        message_for_agent_5 = types.Content(role="user", parts=[types.Part(text=combined_input_for_agent_5)])
        agent_5_output = ""
        async for event in runner_5.run_async(session_id=session_id, user_id=user_id, new_message=message_for_agent_5):
            if event.content and event.content.parts:
                agent_5_output += "".join(part.text for part in event.content.parts if part.text)

        logger.info("Парсинг финального JSON ответа от агента...")
        try:
            clean_json_str_4 = agent_4_output.strip().replace("```json", "").replace("```", "").strip()
            topics_data = json.loads(clean_json_str_4)

            clean_json_str_5 = agent_5_output.strip().replace("```json", "").replace("```", "").strip()
            report_data = json.loads(clean_json_str_5)

            full_report = FullReport(**report_data)

            return ResultsAnalysis(
                message="Interview analysis completed successfully",
                report=full_report
            )
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON: {e}")
            logger.error(f"Проблемный JSON от Агента 4: {agent_4_output}")
            logger.error(f"Проблемный JSON от Агента 5: {agent_5_output}")
            raise ValueError("AI-сервис вернул некорректный формат данных.")
