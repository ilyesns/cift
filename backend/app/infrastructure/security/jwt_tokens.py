from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt

from app.domain.auth import AccessClaims, AccessToken
from app.domain.exceptions import UnauthenticatedError
from app.domain.users import Role, User


class JwtAccessTokenIssuer:
    def __init__(self, *, secret: str, algorithm: str, ttl: timedelta) -> None:
        self._secret = secret
        self._algorithm = algorithm
        self._ttl = ttl

    def issue(self, user: User) -> AccessToken:
        now = datetime.now(UTC)
        payload = {
            "sub": str(user.id),
            "roles": sorted(r.value for r in user.roles),
            "type": "access",
            "iat": now,
            "exp": now + self._ttl,
        }
        token = jwt.encode(payload, self._secret, algorithm=self._algorithm)
        return AccessToken(token=token, expires_in=int(self._ttl.total_seconds()))

    def decode(self, token: str) -> AccessClaims:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
            if payload.get("type") != "access":
                raise ValueError("not an access token")
            return AccessClaims(
                user_id=UUID(payload["sub"]),
                roles=frozenset(Role(r) for r in payload.get("roles", [])),
            )
        except jwt.ExpiredSignatureError as exc:
            raise UnauthenticatedError("Your session has expired.", code="token_expired") from exc
        except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
            raise UnauthenticatedError("Invalid access token.", code="invalid_token") from exc
