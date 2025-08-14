from pydantic_settings import BaseSettings, SettingsConfigDict


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
    google_application_credentials: str


settings = Settings()
