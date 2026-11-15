from fastapi import APIRouter, Request, Response, status
from fastapi.responses import JSONResponse

from app.api.deps import AuthServiceDep, EmailLimiterDep, LoginLimiterDep, SettingsDep
from app.api.errors import error_body
from app.api.v1.schemas.auth import (
    EmailIn,
    LoginIn,
    MessageOut,
    RegisterIn,
    ResetPasswordIn,
    SessionOut,
    TokenIn,
)
from app.api.v1.schemas.users import UserOut
from app.core.config import Settings
from app.domain.auth import AuthResult
from app.domain.exceptions import UnauthenticatedError
from app.domain.i18n import locale_from_accept_language

router = APIRouter(prefix="/auth", tags=["auth"])

# The refresh cookie is only ever sent to /auth endpoints
COOKIE_PATH = "/api/v1/auth"


def _client_key(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _user_agent(request: Request) -> str | None:
    value = request.headers.get("user-agent")
    return value[:255] if value else None


def _set_refresh_cookie(response: Response, settings: Settings, result: AuthResult) -> None:
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=result.refresh_token,
        max_age=settings.refresh_token_ttl_days * 86400,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path=COOKIE_PATH,
    )


def _clear_refresh_cookie(response: Response, settings: Settings) -> None:
    response.delete_cookie(
        key=settings.refresh_cookie_name,
        path=COOKIE_PATH,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
    )


def _session(response: Response, settings: Settings, result: AuthResult) -> SessionOut:
    _set_refresh_cookie(response, settings, result)
    return SessionOut(
        access_token=result.access_token.token,
        expires_in=result.access_token.expires_in,
        user=UserOut.from_domain(result.user),
    )


@router.post("/register", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def register(
    body: RegisterIn,
    request: Request,
    response: Response,
    service: AuthServiceDep,
    settings: SettingsDep,
) -> SessionOut:
    locale = body.preferred_locale or locale_from_accept_language(
        request.headers.get("accept-language")
    )
    result = service.register(
        email=body.email,
        password=body.password,
        full_name=body.full_name,
        locale=locale,
        user_agent=_user_agent(request),
    )
    return _session(response, settings, result)


@router.post("/login", response_model=SessionOut)
def login(
    body: LoginIn,
    request: Request,
    response: Response,
    service: AuthServiceDep,
    settings: SettingsDep,
    limiter: LoginLimiterDep,
) -> SessionOut:
    key = _client_key(request)
    limiter.check(key)
    try:
        result = service.login(
            email=body.email, password=body.password, user_agent=_user_agent(request)
        )
    except UnauthenticatedError:
        limiter.record(key)
        raise
    limiter.reset(key)
    return _session(response, settings, result)


@router.post("/refresh", response_model=SessionOut)
def refresh(
    request: Request, response: Response, service: AuthServiceDep, settings: SettingsDep
) -> SessionOut | JSONResponse:
    raw = request.cookies.get(settings.refresh_cookie_name)
    try:
        result = service.refresh(raw, user_agent=_user_agent(request))
    except UnauthenticatedError as exc:
        failure = JSONResponse(status_code=401, content=error_body(exc.code, exc.message))
        # "session_rotated" means a parallel request already set a newer cookie: keep it
        if exc.code != "session_rotated":
            _clear_refresh_cookie(failure, settings)
        return failure
    return _session(response, settings, result)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, service: AuthServiceDep, settings: SettingsDep) -> Response:
    service.logout(request.cookies.get(settings.refresh_cookie_name))
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    _clear_refresh_cookie(response, settings)
    return response


@router.post("/verify-email", response_model=UserOut)
def verify_email(body: TokenIn, service: AuthServiceDep) -> UserOut:
    return UserOut.from_domain(service.verify_email(body.token))


@router.post(
    "/resend-verification", response_model=MessageOut, status_code=status.HTTP_202_ACCEPTED
)
def resend_verification(
    body: EmailIn, request: Request, service: AuthServiceDep, limiter: EmailLimiterDep
) -> MessageOut:
    key = _client_key(request)
    limiter.check(key)
    limiter.record(key)
    service.resend_verification(body.email)
    return MessageOut(message="If the account needs confirming, a new link is on its way.")


@router.post("/forgot-password", response_model=MessageOut, status_code=status.HTTP_202_ACCEPTED)
def forgot_password(
    body: EmailIn, request: Request, service: AuthServiceDep, limiter: EmailLimiterDep
) -> MessageOut:
    key = _client_key(request)
    limiter.check(key)
    limiter.record(key)
    service.forgot_password(body.email)
    return MessageOut(message="If an account exists for this email, a reset link is on its way.")


@router.post("/reset-password", response_model=MessageOut)
def reset_password(body: ResetPasswordIn, service: AuthServiceDep) -> MessageOut:
    service.reset_password(body.token, body.password)
    return MessageOut(message="Password updated. You can now sign in.")