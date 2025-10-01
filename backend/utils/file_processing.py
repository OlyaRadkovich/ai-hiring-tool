import io
import re
import asyncio
import tempfile
import os
from loguru import logger

from pypdf import PdfReader
import docx
import assemblyai as aai
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
    Transcribes an audio file from the specified path.
    """
    logger.info(f"Starting audio transcription ({audio_path}) via AssemblyAI...")

    config = aai.TranscriptionConfig(language_detection=True)
    transcriber = aai.Transcriber(config=config)

    def sync_transcribe_task():
        logger.info("Running synchronous transcription task in a separate thread...")
        return transcriber.transcribe(audio_path)

    transcript = await asyncio.to_thread(sync_transcribe_task)

    if transcript.status == aai.TranscriptStatus.error:
        logger.error(f"AssemblyAI transcription error: {transcript.error}")
        raise ValueError(f"Transcription failed: {transcript.error}")

    logger.success("AssemblyAI transcription completed successfully.")

    if not transcript.text:
        logger.warning("Transcription returned empty text.")

    return transcript.text or ""