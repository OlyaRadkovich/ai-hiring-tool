import os
import json
import io
import re
import asyncio
from loguru import logger

from backend.api.models import PreparationAnalysis, ResultsAnalysis, ScoreBreakdown
from ..core.config import settings

from backend.agents.pipeline_1_pre_interview.agent_1_data_parser import agent_1_data_parser
from backend.agents.pipeline_1_pre_interview.agent_2_profiler import agent_2_profiler
from backend.agents.pipeline_1_pre_interview.agent_3_plan_generator import agent_3_plan_generator
from backend.agents.pipeline_2_post_interview.agent_4_data_extractor import agent_4_data_extractor

import assemblyai as aai
from pypdf import PdfReader
import docx
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


class AnalysisService:
    """Service responsible for interview analysis business logic using AI Agents"""

    def __init__(self):
        aai.settings.api_key = settings.assemblyai_api_key
        if not aai.settings.api_key:
            logger.warning("API ключ для AssemblyAI не настроен в .env файле!")
        else:
            logger.success("Клиент AssemblyAI сконфигурирован.")

        self.drive_service = None
        try:
            credentials_path = settings.google_application_credentials

            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            self.drive_service = build('drive', 'v3', credentials=credentials)
            logger.success("Клиент Google Drive API успешно инициализирован.")
        except Exception as e:
            logger.error(f"Ошибка инициализации клиента Google Drive API: {e}")

    def _get_google_drive_file_id(self, link: str) -> str:
        """Извлекает ID файла из ссылки на Google Drive."""
        match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', link)
        if match:
            return match.group(1)
        raise ValueError("Некорректная ссылка на Google Drive. Не удалось извлечь ID файла.")

    async def _download_audio_from_drive(self, file_id: str) -> io.BytesIO:
        """
        Асинхронно загружает файл из Google Drive, используя синхронную библиотеку.
        """
        if not self.drive_service:
            raise ConnectionError("Сервис Google Drive не инициализирован. Проверьте учетные данные.")

        logger.info(f"Начало загрузки файла с ID: {file_id} из Google Drive.")

        try:
            request = self.drive_service.files().get_media(fileId=file_id)
            file_io = io.BytesIO()
            downloader = MediaIoBaseDownload(file_io, request)

            def download_in_thread():
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        logger.info(f"Прогресс загрузки: {int(status.progress() * 100)}%.")

            await asyncio.to_thread(download_in_thread)

            logger.success(f"Файл {file_id} успешно загружен.")
            file_io.seek(0)
            return file_io

        except Exception as e:
            logger.error(f"Не удалось скачать файл из Google Drive: {e}")
            raise IOError(f"Ошибка при скачивании файла с Google Drive. "
                          f"Убедитесь, что вы поделились файлом с email вашего сервисного аккаунта.")

    async def _transcribe_audio_assemblyai(self, audio_data: io.BytesIO) -> str:
        """
        Транскрибирует аудио с помощью AssemblyAI SDK, автоматически определяя язык.
        """
        logger.info("Начало транскрипции аудио через AssemblyAI с автоопределением языка...")

        config = aai.TranscriptionConfig(language_detection=True)
        transcriber = aai.Transcriber(config=config)
        transcript = await transcriber.transcribe_async(audio_data)

        if transcript.status == aai.TranscriptStatus.error:
            logger.error(f"Ошибка транскрипции AssemblyAI: {transcript.error}")
            raise ValueError(f"Transcription failed: {transcript.error}")

        detected_language = transcript.language_code
        confidence = transcript.language_confidence or 0
        logger.success(f"Транскрипция AssemblyAI успешно завершена. "
                       f"Определен язык: {detected_language} (уверенность: {confidence:.2f})")

        if confidence < 0.7:
            logger.warning(f"Низкая уверенность в определении языка ({confidence:.2f}). "
                           f"Результат может быть неточным.")

        return transcript.text or ""

    # PIPELINE 1

    async def analyze_preparation(self, profile: str, cv_file: io.BytesIO, filename: str) -> PreparationAnalysis:
        logger.info("Начало процесса подготовки к интервью...")

        api_key_to_use = settings.google_api_key
        if not api_key_to_use:
            logger.error("Google API key не предоставлен.")
            raise ValueError("Google API key is not provided.")

        # ---Устанавливаем API ключ как переменную окружения ---
        os.environ['GOOGLE_API_KEY'] = api_key_to_use
        logger.success("API ключ Google установлен как переменная окружения.")

        logger.info(f"Извлечение текста из файла: {filename}")
        cv_text = ""
        try:
            if filename.lower().endswith('.pdf'):
                reader = PdfReader(cv_file)
                cv_text = "\n".join(page.extract_text() or "" for page in reader.pages)
                logger.success("Текст из PDF успешно извлечен.")
            elif filename.lower().endswith('.docx'):
                doc = docx.Document(cv_file)
                full_text = []
                for para in doc.paragraphs:
                    if para.text.strip():
                        full_text.append(para.text)
                full_text.append("\n--- Табличные данные ---\n")
                for table in doc.tables:
                    for row in table.rows:
                        row_text = " | ".join(cell.text for cell in row.cells)
                        if row_text.strip():
                            full_text.append(row_text)
                    full_text.append("\n")
                cv_text = "\n".join(full_text)
                logger.success("Текст из DOCX успешно извлечен.")
            else:
                cv_text = cv_file.read().decode('utf-8', errors='ignore')
                logger.success("Файл прочитан как текстовый.")
        except Exception as e:
            logger.error(f"Ошибка при чтении файла {filename}: {e}")
            raise ValueError(f"Could not process file: {filename}")

        logger.debug(f"Извлеченный текст резюме (первые 200 символов): {cv_text[:200]}...")

        # TODO: Заменить на динамические ID для многопользовательского режима
        session_service = InMemorySessionService()
        session_id = "preparation_session_123"
        user_id = "prep_user"
        await session_service.create_session(app_name=settings.app_name, user_id=user_id, session_id=session_id)

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

        logger.info("🚀 Запуск agent_2_profiler...")
        runner_2 = Runner(agent=agent_2_profiler, app_name=settings.app_name, session_service=session_service)
        message_for_agent_2 = types.Content(role="user", parts=[types.Part(text=agent_1_output)])
        agent_2_output = ""
        async for event in runner_2.run_async(session_id=session_id, user_id=user_id, new_message=message_for_agent_2):
            if event.content and event.content.parts:
                agent_2_output += "".join(part.text for part in event.content.parts if part.text)

        logger.success("✅ agent_2_profiler завершил работу.")
        logger.debug(f"Выходные данные Агента 2 (Текстовый профиль):\n{agent_2_output}")

        logger.info("🚀 Запуск agent_3_plan_generator...")
        runner_3 = Runner(agent=agent_3_plan_generator, app_name=settings.app_name, session_service=session_service)
        message_for_agent_3 = types.Content(role="user", parts=[types.Part(text=agent_2_output)])
        final_output = ""
        async for event in runner_3.run_async(session_id=session_id, user_id=user_id, new_message=message_for_agent_3):
            if event.content and event.content.parts:
                final_output += "".join(part.text for part in event.content.parts if part.text)

        logger.success("✅ agent_3_plan_generator завершил работу.")
        logger.debug(f"Финальные выходные данные от Агента 3:\n{final_output}")

        logger.info("Парсинг финального вывода в объект Pydantic...")
        try:
            clean_json_str = final_output.strip().replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json_str)

            data["message"] = "Interview preparation plan created successfully."

            result = PreparationAnalysis(**data)
            logger.success("Процесс подготовки к интервью успешно завершен.")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON от Агента 3: {e}")
            logger.error(f"Полученный текст: {final_output}")
            raise ValueError("AI-сервис вернул некорректный формат данных.")

    # PIPELINE 2

    async def analyze_results(self, video_link: str, matrix_content: bytes) -> ResultsAnalysis:
        """
        Анализирует результаты интервью, запуская пайплайн 2.
        """
        logger.info("🚀 Запуск Пайплайна 2: Анализ результатов интервью...")
        try:
            file_id = self._get_google_drive_file_id(video_link)
            audio_file_stream = await self._download_audio_from_drive(file_id)
            transcription_text = await self._transcribe_audio_assemblyai(audio_file_stream)

            logger.info(f"Получена транскрипция (первые 100 символов): {transcription_text[:100]}...")

        except Exception as e:
            logger.error(f"Ошибка на этапе извлечения данных (Агент 4): {e}")
            raise ValueError(f"Ошибка обработки видео или транскрипции: {e}")

        # --- Последующие агенты (пока заглушки) ---
        # Здесь будут вызовы Агентов 5, 6, 7

        logger.success("✅ Пайплайн 2 успешно завершил работу (с заглушками).")

        # Мокаем финальный результат для демонстрации
        return ResultsAnalysis(
            message="Interview analysis completed successfully",
            transcription=transcription_text,
            scores=ScoreBreakdown(
                technical=90, communication=85, leadership=88, cultural=80, overall=85
            ),
            strengths=["Отличные знания в области проектирования систем.", "Сильные коммуникативные навыки."],
            concerns=["Недостаточно глубокий опыт в докере.", "Требует больше самостоятельности."],
            recommendation="RECOMMEND HIRE",
            reasoning="Кандидат показал себя как сильный технический специалист с хорошим потенциалом роста.",
            topicsDiscussed=["Микросервисы", "Базы данных", "Опыт в команде"]
        )
