"""Configuration management for Märchenweber backend."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    mongodb_uri: str
    openrouter_api_key: str
    fastapi_port: int = 8000
    dev_mode: bool = False  # Skip image generation for faster testing

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields from .env (e.g., GLOBAL_SITE_PASSWORD)
    )


settings = Settings()
