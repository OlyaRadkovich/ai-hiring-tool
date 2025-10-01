import io
import re
import asyncio
from loguru import logger

from pypdf import PdfReader
import docx
import assemblyai as aai
from googleapiclient.http import MediaIoBaseDownload


def get_google_drive_file_id(link: str) -> str:
    """
    Извлекает ID файла из ссылки на Google Drive.
    """
    patterns = [
        r'/file/d/([a-zA-Z0-9_-]+)',
        r'/spreadsheets/d/([a-zA-Z0-9_-]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, link)
        if match:
            return match.group(1)
    raise ValueError("Invalid Google Drive link. Could not extract file ID.")


async def download_sheet_from_drive(drive_service, file_id: str) -> str:
    """
    Downloads a Google Sheet as CSV and returns its text content.
    """
    if not drive_service:
        raise ConnectionError("Google Drive service is not initialized.")
    logger.info(f"Starting download of sheet with ID: {file_id} from Google Drive.")
    try:
        request = drive_service.files().export_media(fileId=file_id, mimeType='text/csv')
        file_io = io.BytesIO()
        downloader = MediaIoBaseDownload(file_io, request)

        def download_in_thread():
            done = False
            while not done:
                _, done = downloader.next_chunk()

        await asyncio.to_thread(download_in_thread)
        logger.success(f"Таблица {file_id} успешно экспортирована в CSV.")
        file_io.seek(0)
        return file_io.read().decode('utf-8')
    except Exception as e:
        logger.error(f"Ошибка при экспорте таблицы из Google Drive: {e}", exc_info=True)
        raise IOError(f"Не удалось загрузить требования из Google Drive: {e}")


async def download_audio_from_drive(drive_service, file_id: str) -> io.BytesIO:
    """
    Асинхронно загружает аудио/видео файл из Google Drive.
    """
    if not drive_service:
        raise ConnectionError("Сервис Google Drive не инициализирован. Проверьте учетные данные.")
    logger.info(f"Начало загрузки файла с ID: {file_id} из Google Drive.")
    try:
        request = drive_service.files().get_media(fileId=file_id)
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
        logger.error(f"Критическая ошибка при попытке скачать файл из Google Drive: {e}", exc_info=True)
        raise e


def read_file_content(file: io.BytesIO, filename: str) -> str:
    """
    Читает содержимое файла (PDF, DOCX, TXT) и возвращает текст.
    """
    logger.info(f"Извлечение текста из файла: {filename}")
    try:
        if filename.lower().endswith('.pdf'):
            reader = PdfReader(file)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        elif filename.lower().endswith('.docx'):
            doc = docx.Document(file)
            full_text = [para.text for para in doc.paragraphs if para.text.strip()]
            return "\n".join(full_text)
        else:
            return file.read().decode('utf-8', errors='ignore')
    except Exception as e:
        logger.error(f"Ошибка при чтении файла {filename}: {e}")
        raise ValueError(f"Could not process file: {filename}")


async def transcribe_audio_assemblyai(audio_data: io.BytesIO) -> str:
    logger.info("Начало транскрипции аудио через AssemblyAI с автоопределением языка...")

    config = aai.TranscriptionConfig(language_detection=True)
    transcriber = aai.Transcriber(config=config)

    def sync_transcribe_task():
        logger.info("Запуск синхронной задачи транскрипции в отдельном потоке...")
        return transcriber.transcribe(audio_data)

    transcript = await asyncio.to_thread(sync_transcribe_task)

    if transcript.status == aai.TranscriptStatus.error:
        logger.error(f"Ошибка транскрипции AssemblyAI: {transcript.error}")
        raise ValueError(f"Transcription failed: {transcript.error}")

    logger.success("Транскрипция AssemblyAI успешно завершена.")

    if not transcript.text:
        logger.warning("Транскрипция вернула пустой текст.")

    return transcript.text or ""