from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "MathVision AI API"
    app_version: str = "0.1.0"
    api_host: str = "0.0.0.0"
    api_port: int = Field(default=8000, ge=1, le=65535)
    log_level: str = "INFO"
    database_url: str = (
        "postgresql+psycopg://mathvision:mathvision@localhost:5432/mathvision"
    )
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:4173"]
    upload_dir: Path = Path("data/runtime/uploads")
    processed_dir: Path = Path("data/runtime/processed")
    model_dir: Path = Path("data/runtime/models")
    max_upload_size_bytes: int = Field(default=10 * 1024 * 1024, ge=1)
    max_image_pixels: int = Field(default=25_000_000, ge=1)
    retention_hours: int = Field(default=24, ge=1)

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"), case_sensitive=False, extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
