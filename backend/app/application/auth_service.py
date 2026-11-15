import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from app.application.security import hash_token, new_opaque_token, utcnow
from app.domain.auth import ActionToken, AuthResult, RefreshSession, TokenPurpose
from app.domain.exceptions import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    UnauthenticatedError,
    ValidationFailedError,
)
from app.domain.i18n import normalize_locale
from app.domain.ports.auth import AccessTokenIssuer, AuthNotifier, PasswordHasher
from app.domain.ports.unit_of_work import UnitOfWork
from app.domain.users import Role, User, normalize_email

logger = logging.getLogger(__name__)

# Two requests can race to refresh the same token (two tabs, a double reload).
# A reuse inside this window is refused without ending the whole session family.
REUSE_GRACE = timedelta(seconds=10)


@dataclass(frozen=True, slots=True)
class AuthPolicy:
    refresh_ttl: timedelta
    verify_email_ttl: timedelta
    reset_password_ttl: timedelta


class AuthService:
    def __init__(
        self,
        *,
        uow: UnitOfWork,
        hasher: PasswordHasher,
        tokens: AccessTokenIssuer,
        notifier: AuthNotifier,
        policy: AuthPolicy,
        now: Callable[[], datetime] = utcnow,
    ) -> None:
        self._uow = uow
        self._hasher = hasher
        self._tokens = tokens
        self._notifier = notifier
        self._policy = policy
        self._now = now

    # --- registration and email verification ---------------------------------

    def register(
        self,
        *,
        email: str,
        password: str,
        full_name: str,
        locale: str,
        user_agent: str | None = None,
    ) -> AuthResult:
        email = normalize_email(email)
        with self._uow as uow:
            if uow.users.get_by_email(email) is not None:
                raise ConflictError("An account with this email already exists.", code="email_taken")
            user = User(
                id=uuid4(),
                email=email,
                password_hash=self._hasher.hash(password),
                full_name=full_name.strip(),
                preferred_locale=normalize_locale(locale),
                preferred_city=None,
                is_active=True,
                email_verified_at=None,
                created_at=self._now(),
                roles=frozenset({Role.MEMBER}),
            )
            uow.users.add(user)
            verify_token = self._new_action_token(
                uow, user.id, TokenPurpose.VERIFY_EMAIL, self._policy.verify_email_ttl
            )
            result = self._start_session(uow, user, family_id=uuid4(), user_agent=user_agent)
            uow.commit()
        self._notify(self._notifier.send_verification, user, verify_token)
        return result

    def verify_email(self, token: str) -> User:
        with self._uow as uow:
            now = self._now()
            record = self._use_action_token(uow, token, TokenPurpose.VERIFY_EMAIL, now)
            user = self._require_user(uow, record.user_id)
            if not user.is_verified:
                uow.users.mark_verified(user.id, now)
            user = self._require_user(uow, user.id)
            uow.commit()
        return user

    def resend_verification(self, email: str) -> None:
        """Always silent, so the endpoint can't be used to discover which emails exist."""
        with self._uow as uow:
            user = uow.users.get_by_email(normalize_email(email))
            if user is None or user.is_verified or not user.is_active:
                return
            token = self._new_action_token(
                uow, user.id, TokenPurpose.VERIFY_EMAIL, self._policy.verify_email_ttl
            )
            uow.commit()
        self._notify(self._notifier.send_verification, user, token)

    # --- sessions ------------------------------------------------------------

    def login(self, *, email: str, password: str, user_agent: str | None = None) -> AuthResult:
        with self._uow as uow:
            user = uow.users.get_by_email(normalize_email(email))
            if user is None or not self._hasher.verify(user.password_hash, password):
                raise UnauthenticatedError(
                    "Email or password is incorrect.", code="invalid_credentials"
                )
            if not user.is_active:
                raise PermissionDeniedError(
                    "This account has been suspended.", code="account_suspended"
                )
            if self._hasher.needs_rehash(user.password_hash):
                uow.users.set_password_hash(user.id, self._hasher.hash(password))
            result = self._start_session(uow, user, family_id=uuid4(), user_agent=user_agent)
            uow.commit()
        return result

    def refresh(self, raw_token: str | None, *, user_agent: str | None = None) -> AuthResult:
        if not raw_token:
            raise UnauthenticatedError("You are not signed in.", code="no_session")
        with self._uow as uow:
            now = self._now()
            current = uow.refresh_sessions.get_by_hash(hash_token(raw_token))
            if current is None:
                raise UnauthenticatedError("Please sign in again.", code="invalid_session")

            if current.revoked_at is not None:
                if now - current.revoked_at <= REUSE_GRACE:
                    raise UnauthenticatedError("Session already refreshed.", code="session_rotated")
                # An old token came back: assume it was stolen and end every session in the chain
                uow.refresh_sessions.revoke_family(current.family_id, now)
                uow.commit()
                raise UnauthenticatedError(
                    "Your session has ended. Please sign in again.", code="session_reused"
                )

            if current.expires_at <= now:
                raise UnauthenticatedError(
                    "Your session has expired. Please sign in again.", code="session_expired"
                )

            user = uow.users.get(current.user_id)
            if user is None or not user.is_active:
                uow.refresh_sessions.revoke_family(current.family_id, now)
                uow.commit()
                raise UnauthenticatedError("Please sign in again.", code="invalid_session")

            uow.refresh_sessions.revoke(current.id, now)
            result = self._start_session(
                uow, user, family_id=current.family_id, user_agent=user_agent
            )
            uow.commit()
        return result

    def logout(self, raw_token: str | None) -> None:
        if not raw_token:
            return
        with self._uow as uow:
            current = uow.refresh_sessions.get_by_hash(hash_token(raw_token))
            if current is not None:
                uow.refresh_sessions.revoke_family(current.family_id, self._now())
                uow.commit()

    # --- password reset --------------------------------------------------------

    def forgot_password(self, email: str) -> None:
        """Always silent, so the endpoint can't be used to discover which emails exist."""
        with self._uow as uow:
            user = uow.users.get_by_email(normalize_email(email))
            if user is None or not user.is_active:
                return
            token = self._new_action_token(
                uow, user.id, TokenPurpose.RESET_PASSWORD, self._policy.reset_password_ttl
            )
            uow.commit()
        self._notify(self._notifier.send_password_reset, user, token)

    def reset_password(self, token: str, new_password: str) -> None:
        with self._uow as uow:
            now = self._now()
            record = self._use_action_token(uow, token, TokenPurpose.RESET_PASSWORD, now)
            user = self._require_user(uow, record.user_id)
            uow.users.set_password_hash(user.id, self._hasher.hash(new_password))
            if not user.is_verified:
                uow.users.mark_verified(user.id, now)  # the link proves they own the inbox
            uow.refresh_sessions.revoke_all_for_user(user.id, now)
            uow.commit()

    # --- helpers -----------------------------------------------------------------

    def _start_session(
        self, uow: UnitOfWork, user: User, *, family_id: UUID, user_agent: str | None
    ) -> AuthResult:
        raw, digest = new_opaque_token()
        expires_at = self._now() + self._policy.refresh_ttl
        uow.refresh_sessions.add(
            RefreshSession(
                id=uuid4(),
                user_id=user.id,
                family_id=family_id,
                token_hash=digest,
                expires_at=expires_at,
                user_agent=user_agent,
            )
        )
        return AuthResult(
            user=user,
            access_token=self._tokens.issue(user),
            refresh_token=raw,
            refresh_expires_at=expires_at,
        )

    def _new_action_token(
        self, uow: UnitOfWork, user_id: UUID, purpose: TokenPurpose, ttl: timedelta
    ) -> str:
        now = self._now()
        uow.action_tokens.invalidate_for_user(user_id, purpose, now)  # only the newest link works
        raw, digest = new_opaque_token()
        uow.action_tokens.add(
            ActionToken(
                id=uuid4(),
                user_id=user_id,
                purpose=purpose,
                token_hash=digest,
                expires_at=now + ttl,
            )
        )
        return raw

    def _use_action_token(
        self, uow: UnitOfWork, raw: str, purpose: TokenPurpose, now: datetime
    ) -> ActionToken:
        record = uow.action_tokens.get_by_hash(hash_token(raw), purpose)
        if record is None or not record.is_usable(now):
            raise ValidationFailedError(
                "This link is invalid or has expired.", code="invalid_or_expired_token"
            )
        uow.action_tokens.mark_used(record.id, now)
        return record

    @staticmethod
    def _require_user(uow: UnitOfWork, user_id: UUID) -> User:
        user = uow.users.get(user_id)
        if user is None:
            raise NotFoundError("User not found.", code="user_not_found")
        return user

    @staticmethod
    def _notify(send: Callable[[User, str], None], user: User, token: str) -> None:
        # The account change is already saved; a mail outage must not undo it.
        # The user can ask for a new link.
        try:
            send(user, token)
        except Exception:
            logger.exception("Could not send %s email to %s", send.__name__, user.email)