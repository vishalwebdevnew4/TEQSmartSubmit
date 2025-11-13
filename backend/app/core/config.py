"""Application configuration settings."""

from functools import lru_cache
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Pydantic settings for the application environment."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", env_prefix="TEQ_")

    app_name: str = "TEQSmartSubmit"
    environment: str = "development"
    debug: bool = True
    secret_key: str = "change-me"
    access_token_expires_minutes: int = 30
    jwt_algorithm: str = "HS256"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/teqsmartsubmit"

    cors_origins: list[str] = ["http://localhost:3000"]
    page_load_timeout: float = 30.0
    submission_delay_seconds: float = 5.0
    retry_limit: int = 2

    playwright_headless: bool = True
    playwright_context_timeout: int = 30000

    redis_url: str | None = None
    admin_registration_token: str | None = None

    def model_post_init(self, __context: Any) -> None:
        """Normalize certain settings after model initialization."""
        self.cors_origins = [origin.strip() for origin in self.cors_origins]


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance."""
    return Settings()

