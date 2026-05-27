"""Application settings loaded from environment variables via pydantic-settings.

All process configuration enters the app through `get_settings()`. The `.env` file
is read in development; in production the same names are set on the deploy box.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Process-wide settings. Field names map to UPPER_SNAKE env vars."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    database_url: str = (
        "postgresql+psycopg://tempest:tempest@localhost:5432/tempest_watch"
    )
    log_level: str = "INFO"

    pokemontcg_api_key: str | None = None
    ebay_app_id: str | None = None
    ebay_cert_id: str | None = None

    llm_api_key: str | None = None
    llm_model: str | None = None

    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Return the cached Settings singleton. The `.env` file is read once per process."""
    return Settings()
