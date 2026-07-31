"""Application configuration via environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Crime Horror Research Engine"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    secret_key: str = Field(default="change-me")
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:5173"

    database_url: str = "postgresql+asyncpg://chre:chre_secret@localhost:5432/chre"
    database_url_sync: str = "postgresql://chre:chre_secret@localhost:5432/chre"

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    elasticsearch_url: str = "http://localhost:9200"
    elasticsearch_index: str = "chre_articles"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ai_provider: Literal["local", "openai"] = "local"

    crawler_user_agent: str = "CHRE-ResearchBot/1.0"
    crawler_rate_limit: float = 2.0
    crawler_concurrent_requests: int = 8
    crawler_proxy_url: str = ""
    crawler_respect_robots: bool = True

    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    encryption_key: str = Field(default="change-me-32-byte-key-for-fernet!!")

    sentry_dsn: str = ""
    log_level: str = "INFO"
    prometheus_enabled: bool = True

    backup_enabled: bool = True
    backup_schedule: str = "0 3 * * *"
    backup_retention_days: int = 30

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
