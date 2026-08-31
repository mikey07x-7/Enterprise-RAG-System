"""
Application Configuration

Loads environment variables from the .env file using Pydantic Settings.
This provides type-safe access to configuration across the application.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --------------------------------------------------
    # Application
    # --------------------------------------------------
    APP_NAME: str = Field(default="Enterprise RAG System")
    APP_VERSION: str = Field(default="1.0.0")
    DEBUG: bool = Field(default=False)

    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)

    # --------------------------------------------------
    # Database
    # --------------------------------------------------
    DATABASE_URL: str

    # --------------------------------------------------
    # Security
    # --------------------------------------------------
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60)

    # --------------------------------------------------
    # Redis
    # --------------------------------------------------
    REDIS_URL: str

    # --------------------------------------------------
    # AI Models
    # --------------------------------------------------
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    # --------------------------------------------------
    # LLM
    # --------------------------------------------------
    GROQ_MODEL: str = "openai/gpt-oss-120b"

    VECTOR_DB: str = "faiss"
    EMBEDDING_MODEL: str = "BAAI/bge-base-en-v1.5"


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.

    The settings are loaded only once during the application's lifetime.
    """
    return Settings()


settings = get_settings()