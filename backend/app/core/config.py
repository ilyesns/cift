from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Values come from environment variables (or a local .env file).

    Lists are written as JSON in the environment, e.g.
    CORS_ORIGINS='["http://localhost:5174"]'
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "CIFT API"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://cift:cift@localhost:5433/cift"
    cors_origins: list[str] = ["http://localhost:5174"]

    default_locale: str = "it"
    supported_locales: list[str] = ["it", "ar", "en"]

    timezone: str = "Europe/Rome"


@lru_cache
def get_settings() -> Settings:
    return Settings()