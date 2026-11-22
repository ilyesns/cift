from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.rate_limit import FailureLimiter
from app.application.account_service import AccountService
from app.application.auth_service import AuthPolicy, AuthService
from app.application.health_service import HealthService
from app.application.timetable_import import TimetableImportService
from app.core.config import Settings
from app.domain.exceptions import PermissionDeniedError, UnauthenticatedError
from app.domain.ports.auth import AccessTokenIssuer, AuthNotifier, PasswordHasher
from app.domain.ports.prayer import SunCalculator
from app.domain.ports.unit_of_work import UnitOfWork
from app.domain.users import Role, User
from app.infrastructure.db.database import Database
from app.infrastructure.db.probe import SqlAlchemyDatabaseProbe
from app.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork

# --- objects built once in main.py -------------------------------------------------


def get_app_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_database(request: Request) -> Database:
    return request.app.state.database


def get_password_hasher(request: Request) -> PasswordHasher:
    return request.app.state.password_hasher


def get_token_issuer(request: Request) -> AccessTokenIssuer:
    return request.app.state.token_issuer


def get_auth_notifier(request: Request) -> AuthNotifier:
    return request.app.state.auth_notifier


def get_auth_policy(request: Request) -> AuthPolicy:
    return request.app.state.auth_policy


def get_login_limiter(request: Request) -> FailureLimiter:
    return request.app.state.login_limiter


def get_email_limiter(request: Request) -> FailureLimiter:
    return request.app.state.email_limiter


SettingsDep = Annotated[Settings, Depends(get_app_settings)]
DatabaseDep = Annotated[Database, Depends(get_database)]
HasherDep = Annotated[PasswordHasher, Depends(get_password_hasher)]
TokenIssuerDep = Annotated[AccessTokenIssuer, Depends(get_token_issuer)]
NotifierDep = Annotated[AuthNotifier, Depends(get_auth_notifier)]
PolicyDep = Annotated[AuthPolicy, Depends(get_auth_policy)]
LoginLimiterDep = Annotated[FailureLimiter, Depends(get_login_limiter)]
EmailLimiterDep = Annotated[FailureLimiter, Depends(get_email_limiter)]

# --- per-request objects ---------------------------------------------------------------


def get_uow(database: DatabaseDep) -> UnitOfWork:
    return SqlAlchemyUnitOfWork(database.session_factory)


UowDep = Annotated[UnitOfWork, Depends(get_uow)]


def get_sun_calculator(request: Request) -> SunCalculator:
    return request.app.state.sun_calculator


SunCalculatorDep = Annotated[SunCalculator, Depends(get_sun_calculator)]


def get_timetable_import_service(uow: UowDep, sun: SunCalculatorDep) -> TimetableImportService:
    return TimetableImportService(uow=uow, sun=sun)


TimetableImportServiceDep = Annotated[TimetableImportService, Depends(get_timetable_import_service)]


def get_health_service(database: DatabaseDep, settings: SettingsDep) -> HealthService:
    return HealthService(
        probe=SqlAlchemyDatabaseProbe(database.engine),
        app_name=settings.app_name,
        environment=settings.environment,
    )


def get_auth_service(
    uow: UowDep,
    hasher: HasherDep,
    tokens: TokenIssuerDep,
    notifier: NotifierDep,
    policy: PolicyDep,
) -> AuthService:
    return AuthService(uow=uow, hasher=hasher, tokens=tokens, notifier=notifier, policy=policy)


def get_account_service(uow: UowDep, hasher: HasherDep) -> AccountService:
    return AccountService(uow=uow, hasher=hasher)


HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]

# --- the signed-in user ----------------------------------------------------------------

_bearer = HTTPBearer(auto_error=False)
BearerDep = Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)]


def get_current_user(credentials: BearerDep, tokens: TokenIssuerDep, uow: UowDep) -> User:
    if credentials is None:
        raise UnauthenticatedError("Please sign in.", code="not_authenticated")
    claims = tokens.decode(credentials.credentials)
    # Load from the database so suspensions and role changes apply immediately
    with uow:
        user = uow.users.get(claims.user_id)
    if user is None or not user.is_active:
        raise UnauthenticatedError("Please sign in again.", code="invalid_token")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_verified(user: CurrentUser) -> User:
    if not user.is_verified:
        raise PermissionDeniedError("Please confirm your email first.", code="email_not_verified")
    return user


def require_roles(*roles: Role) -> Callable[[User], User]:
    def checker(user: CurrentUser) -> User:
        if not user.has_any_role(*roles):
            raise PermissionDeniedError("You don't have permission to do this.", code="forbidden")
        return user

    return checker


VerifiedUser = Annotated[User, Depends(require_verified)]
AdminUser = Annotated[User, Depends(require_roles(Role.ADMIN))]
EditorUser = Annotated[User, Depends(require_roles(Role.EDITOR, Role.ADMIN))]
