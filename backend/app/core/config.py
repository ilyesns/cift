from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_JWT_SECRET = "dev-only-change-me"


class Settings(BaseSettings):
    """Values come from environment variables (or a local .env file).

    Lists are written as JSON in the environment, e.g.
    CORS_ORIGINS='["http://localhost:5174"]'
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "CIFT API"
    environment: str = "development"

    database_url: str = "postgresql+psycopg://cift:cift@localhost:5433/cift"
    db_echo: bool = False

    cors_origins: list[str] = ["http://localhost:5174"]

    default_locale: str = "it"
    supported_locales: list[str] = ["it", "ar", "en"]
    timezone: str = "Europe/Rome"

    # Auth
    jwt_secret: str = DEFAULT_JWT_SECRET
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 30
    verify_email_ttl_hours: int = 24
    reset_password_ttl_minutes: int = 60
    refresh_cookie_name: str = "cift_refresh"
    cookie_secure: bool = False  # True in production (HTTPS only)
    login_max_failures_per_minute: int = 5

    # Links inside emails point to the website
    web_url: str = "http://localhost:5174"

    # Email
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_starttls: bool = False
    email_from: str = "CIFT <noreply@example.com>"


@lru_cache
def get_settings() -> Settings:
    return Settings()