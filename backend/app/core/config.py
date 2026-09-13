from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    AI_CORE_URL: str = "http://localhost:8001"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/servicedesk_radar"


settings = Settings()

