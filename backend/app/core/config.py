from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    AI_CORE_URL: str = "http://localhost:8001"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/servicedesk_radar"
    DB_IS_ACTIVE: bool = False

    JWT_SECRET_KEY: str = "DarkNight" #TODO: در نسخه نهایی باید از فایل .env خوانده بشه
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


settings = Settings()

