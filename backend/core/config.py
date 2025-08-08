from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "InterviewAI Backend"
    api_prefix: str = "/api"
    cors_origins: list[str] = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


