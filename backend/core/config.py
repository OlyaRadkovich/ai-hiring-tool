import os
import base64
import tempfile
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "InterviewAI Backend"
    api_prefix: str = "/api"
    cors_origins: list[str] = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:8083",
        "http://127.0.0.1:8083",
    ]

    google_api_key: str
    assemblyai_api_key: str

    google_application_b64: str

    @model_validator(mode='after')
    def generate_credentials_file(self) -> 'Settings':
        if self.google_application_b64:
            decoded_bytes = base64.b64decode(self.google_application_b64)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
                temp_file.write(decoded_bytes)
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_file.name
                
        return self

settings = Settings()
