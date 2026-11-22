from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.errors import register_error_handlers
from app.api.rate_limit import FailureLimiter
from app.api.v1.router import api_router
from app.application.auth_service import AuthPolicy
from app.core.config import DEFAULT_JWT_SECRET, Settings, get_settings
from app.infrastructure.db.database import Database
from app.infrastructure.email.auth_notifier import EmailAuthNotifier
from app.infrastructure.email.smtp import SmtpEmailSender
from app.infrastructure.security.jwt_tokens import JwtAccessTokenIssuer
from app.infrastructure.security.passwords import Argon2PasswordHasher


def build_services(app: FastAPI, settings: Settings) -> None:
    """Composition root: the one place that picks concrete implementations for the ports."""
    app.state.password_hasher = Argon2PasswordHasher()
    app.state.token_issuer = JwtAccessTokenIssuer(
        secret=settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
        ttl=timedelta(minutes=settings.access_token_ttl_minutes),
    )
    app.state.auth_notifier = EmailAuthNotifier(
        sender=SmtpEmailSender(
            host=settings.smtp_host,
            port=settings.smtp_port,
            sender=settings.email_from,
            username=settings.smtp_user,
            password=settings.smtp_password,
            starttls=settings.smtp_starttls,
        ),
        web_url=settings.web_url,
        verify_ttl_hours=settings.verify_email_ttl_hours,
        reset_ttl_minutes=settings.reset_password_ttl_minutes,
    )
    app.state.auth_policy = AuthPolicy(
        refresh_ttl=timedelta(days=settings.refresh_token_ttl_days),
        verify_email_ttl=timedelta(hours=settings.verify_email_ttl_hours),
        reset_password_ttl=timedelta(minutes=settings.reset_password_ttl_minutes),
    )
    app.state.login_limiter = FailureLimiter(settings.login_max_failures_per_minute, 60)
    app.state.email_limiter = FailureLimiter(3, 60)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    if settings.environment == "production" and settings.jwt_secret == DEFAULT_JWT_SECRET:
        raise RuntimeError("Set JWT_SECRET before running in production.")

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.database = Database(settings.database_url, echo=settings.db_echo)
        try:
            yield
        finally:
            app.state.database.dispose()

    app = FastAPI(title=settings.app_name, version="0.2.0", docs_url="/docs", lifespan=lifespan)
    app.state.settings = settings
    build_services(app, settings)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_error_handlers(app)
    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
