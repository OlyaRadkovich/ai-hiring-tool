import io
import re
import asyncio
import tempfile
import os
import time

from loguru import logger

from assemblyai import api
from pypdf import PdfReader
import docx
import assemblyai as aai
from assemblyai.client import Client as AssemblyAIClient
from assemblyai.types import Settings as AssemblyAISettings
from googleapiclient.http import MediaIoBaseDownload


def get_google_drive_file_id(link: str) -> str:
    """
    Extracts the file ID from a Google Drive link.
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
        logger.success(f"Sheet {file_id} successfully exported to CSV.")
        file_io.seek(0)
        return file_io.read().decode('utf-8')
    except Exception as e:
        logger.error(f"Error exporting sheet from Google Drive: {e}", exc_info=True)
        raise IOError(f"Failed to download requirements from Google Drive: {e}")


async def download_audio_from_drive_to_temp_file(drive_service, file_id: str) -> str:
    """
    Asynchronously downloads an audio/video file from Google Drive to a temporary file on disk.
    Returns the path to the temporary file.
    """
    if not drive_service:
        raise ConnectionError("Google Drive service not initialized. Check credentials.")
    logger.info(f"Starting download of file with ID: {file_id} from Google Drive to disk.")
    try:
        request = drive_service.files().get_media(fileId=file_id)

        fd, temp_file_path = tempfile.mkstemp()

        with os.fdopen(fd, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)

            def download_in_thread():
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        logger.info(f"Download progress: {int(status.progress() * 100)}%.")

            await asyncio.to_thread(download_in_thread)

        logger.success(f"File {file_id} successfully downloaded to temporary file: {temp_file_path}")
        return temp_file_path
    except Exception as e:
        logger.error(f"Critical error while trying to download file from Google Drive: {e}", exc_info=True)
        raise e


def read_file_content(file: io.BytesIO, filename: str) -> str:
    """
    Reads the content of a file (PDF, DOCX, TXT) and returns the text.
    """
    logger.info(f"Extracting text from file: {filename}")
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
        logger.error(f"Error reading file {filename}: {e}")
        raise ValueError(f"Could not process file: {filename}")


async def transcribe_audio_assemblyai(audio_path: str) -> str:
    """
    Transcribes an audio file with enhanced logging, using the correct low-level API
    functions and public properties.
    """
    logger.info(f"Starting audio transcription process for file: {audio_path}")

    # --- Проверка файла ---
    try:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file for transcription not found at {audio_path}")
        file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
        logger.info(f"Source file found. Size: {file_size_mb:.2f} MB.")
    except Exception as e:
        logger.error(f"Failed to access source file at {audio_path}: {e}")
        raise

    # --- Настройка клиента ---
    custom_settings = AssemblyAISettings(http_timeout=900.0)
    api_client = AssemblyAIClient(settings=custom_settings)
    transcriber = aai.Transcriber(client=api_client)
    config = aai.TranscriptionConfig(language_detection=True)

    submitted_transcript = None
    try:
        # --- ЭТАП 1: Отправка файла ---
        def sync_submit_task():
            logger.info("Step 1/2: Submitting file to AssemblyAI...")
            # submit() возвращает полноценный объект Transcript
            return transcriber.submit(audio_path, config=config)

        submitted_transcript = await asyncio.to_thread(sync_submit_task)
        # ИСПОЛЬЗУЕМ ПУБЛИЧНЫЕ СВОЙСТВА .id и .status
        logger.success(
            f"Step 1/2: File submitted. Job ID: {submitted_transcript.id}. Status: {submitted_transcript.status}")

        # --- ЭТАП 2: Опрос статуса в цикле ---
        def sync_poll_task():
            logger.info("Step 2/2: Polling for transcription result...")
            polling_interval = 20  # seconds

            while True:
                # Используем ID из публичного свойства .id
                current_transcript_response = api.get_transcript(
                    api_client.http_client,
                    submitted_transcript.id
                )

                status = current_transcript_response.status
                logger.info(f"Polling... Current job status: {status.value}")

                if status in [aai.TranscriptStatus.completed, aai.TranscriptStatus.error]:
                    logger.info(f"Polling finished with status '{status.value}'.")
                    return current_transcript_response

                time.sleep(polling_interval)

        final_transcript_response = await asyncio.to_thread(sync_poll_task)

        if final_transcript_response.status == aai.TranscriptStatus.error:
            raise ValueError(f"Transcription failed: {final_transcript_response.error}")

        logger.success("Step 2/2: AssemblyAI transcription completed successfully.")

        if not final_transcript_response.text:
            logger.warning("Transcription returned empty text.")

        return final_transcript_response.text or ""

    except Exception as e:
        logger.error(f"An error occurred during the transcription process: {e}", exc_info=True)
        if submitted_transcript:
            try:
                def sync_delete_task():
                    logger.warning(f"Attempting to delete failed transcription job {submitted_transcript.id}...")
                    # Используем ID из публичного свойства .id
                    api.delete_transcript(
                        api_client.http_client,
                        submitted_transcript.id
                    )

                await asyncio.to_thread(sync_delete_task)
                logger.success("Failed job deleted successfully.")
            except Exception as delete_e:
                logger.error(f"Could not delete failed job {submitted_transcript.id}: {delete_e}")
        raise


def extract_json_from_string(text: str) -> str:
    """
    Finds and extracts the first JSON object from a string, stripping markdown code blocks.
    """

    text = text.strip().replace("```json", "").replace("```", "").strip()

    start_index = text.find('{')
    end_index = text.rfind('}')

    if start_index != -1 and end_index != -1 and end_index > start_index:
        return text[start_index:end_index + 1]

    return text
