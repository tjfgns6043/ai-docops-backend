"""Model server settings."""

from functools import lru_cache
from os import getenv
from typing import Any

from pydantic import BaseModel, Field

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ModuleNotFoundError:  # pragma: no cover
    SettingsConfigDict = dict  # type: ignore[misc,assignment]

    class BaseSettings(BaseModel):  # type: ignore[no-redef]
        """Small fallback for local test environments."""

        def __init__(self, **data: Any) -> None:
            env_data = {
                name: getenv(name.upper(), field.default)
                for name, field in self.__class__.model_fields.items()
                if name not in data
            }
            env_data.update(data)
            super().__init__(**env_data)


class Settings(BaseSettings):
    """Runtime settings for the model server."""

    app_env: str = Field(default="local")
    service_name: str = Field(default="model-server")
    log_level: str = Field(default="INFO")
    model_name: str = Field(default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    model_device: str = Field(default="cpu")
    model_version: str = Field(default="multilingual-minilm-l12-v1")
    embedding_dimension: int = Field(default=384)
    preprocess_version: str = Field(default="text-preprocess-v1")
    allow_model_fallback: bool = Field(default=False)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Return cached model server settings."""
    return Settings()
