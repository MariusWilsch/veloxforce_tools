"""
Settings for OpenRouter Tools.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """
    Settings for OpenRouter Tools.

    Attributes:
        env: Environment (DEVELOPMENT or PRODUCTION)
        max_retries: Optional explicit override for max retries
    """

    # Environment: DEVELOPMENT or PRODUCTION
    ENV: Literal["DEVELOPMENT", "PRODUCTION"] = "DEVELOPMENT"

    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    OPENROUTER_API_KEY: Optional[str] = None

    MAX_RETRIES: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # This is the key change - ignore extra fields
    )


# Create a cached instance of Settings to avoid reloading
@lru_cache()
def get_settings() -> Settings:
    """
    Get the settings instance (cached).

    Returns:
        Settings: The settings instance
    """
    return Settings()
