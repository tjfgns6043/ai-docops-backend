"""API service settings."""

from functools import lru_cache
from os import getenv
from typing import Any

from pydantic import BaseModel, Field

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ModuleNotFoundError:  # pragma: no cover - exercised only without dev deps installed
    SettingsConfigDict = dict  # type: ignore[misc,assignment]

    class BaseSettings(BaseModel):  # type: ignore[no-redef]
        """Small local fallback when pydantic-settings is not installed."""

        def __init__(self, **data: Any) -> None:
            env_data = {
                name: getenv(name.upper(), field.default)
                for name, field in self.__class__.model_fields.items()
                if name not in data
            }
            env_data.update(data)
            super().__init__(**env_data)


class Settings(BaseSettings):
    """Runtime settings for the API service."""

    app_env: str = Field(default="local")
    service_name: str = Field(default="api")
    log_level: str = Field(default="INFO")
    dev_api_key: str = Field(default="ak_dev_tenant_a_123456")
    dev_tenant_id: str = Field(default="00000000-0000-0000-0000-00000000000a")
    dev_owner_id: str = Field(default="00000000-0000-0000-0000-0000000000aa")
    database_url: str = Field(default="postgresql+asyncpg://app:app@postgres:5432/app")
    redis_url: str = Field(default="redis://redis:6379/0")
    model_server_url: str = Field(default="http://model-server:9000")
    model_version: str = Field(default="multilingual-minilm-l12-v1")
    preprocess_version: str = Field(default="text-preprocess-v1")
    model_connect_timeout_seconds: float = Field(default=1.0)
    model_read_timeout_seconds: float = Field(default=5.0)
    model_write_timeout_seconds: float = Field(default=1.0)
    model_pool_timeout_seconds: float = Field(default=1.0)
    readiness_checks_enabled: bool = Field(default=False)
    allow_dev_auth_fallback: bool = Field(default=True)
    cache_ttl_summary_seconds: int = Field(default=300)
    cache_ttl_prediction_seconds: int = Field(default=300)
    cache_ttl_query_embedding_seconds: int = Field(default=600)
    cache_ttl_search_seconds: int = Field(default=60)
    rate_limit_window_seconds: int = Field(default=60)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Return cached API settings."""
    return Settings()
