"""Worker settings."""

from functools import lru_cache
from os import getenv
from typing import Any

from pydantic import BaseModel, Field

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ModuleNotFoundError:  # pragma: no cover
    SettingsConfigDict = dict  # type: ignore[misc,assignment]

    class BaseSettings(BaseModel):  # type: ignore[no-redef]
        """Small fallback for local tests."""

        def __init__(self, **data: Any) -> None:
            env_data = {
                name: getenv(name.upper(), field.default)
                for name, field in self.__class__.model_fields.items()
                if name not in data
            }
            env_data.update(data)
            super().__init__(**env_data)


class Settings(BaseSettings):
    """Runtime worker settings."""

    app_env: str = Field(default="local")
    log_level: str = Field(default="INFO")
    database_url: str = Field(default="postgresql+asyncpg://app:app@postgres:5432/app")
    celery_broker_url: str = Field(default="redis://redis:6379/1")
    celery_result_backend: str = Field(default="redis://redis:6379/2")
    model_server_url: str = Field(default="http://model-server:9000")
    model_version: str = Field(default="multilingual-minilm-l12-v1")
    preprocess_version: str = Field(default="text-preprocess-v1")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Return cached settings."""
    return Settings()
