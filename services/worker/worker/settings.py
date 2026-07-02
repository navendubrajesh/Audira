"""Worker configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "postgresql+asyncpg://audira:audira@localhost:5432/audira"
    environment: str = "development"

    inference_base_url: str = ""
    inference_api_key: str = ""
    worker_max_jobs: int = 10


settings = Settings()
