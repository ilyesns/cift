from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.domain.auth import ActionToken, RefreshSession, TokenPurpose
from app.infrastructure.db.models.auth import ActionTokenModel, RefreshSessionModel


class SqlAlchemyActionTokenRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, token: ActionToken) -> None:
        self._session.add(
            ActionTokenModel(
                id=token.id,
                user_id=token.user_id,
                purpose=token.purpose.value,
                token_hash=token.token_hash,
                expires_at=token.expires_at,
                used_at=token.used_at,
            )
        )

    def get_by_hash(self, token_hash: str, purpose: TokenPurpose) -> ActionToken | None:
        row = self._session.scalar(
            select(ActionTokenModel).where(
                ActionTokenModel.token_hash == token_hash,
                ActionTokenModel.purpose == purpose.value,
            )
        )
        if row is None:
            return None
        return ActionToken(
            id=row.id,
            user_id=row.user_id,
            purpose=TokenPurpose(row.purpose),
            token_hash=row.token_hash,
            expires_at=row.expires_at,
            used_at=row.used_at,
        )

    def mark_used(self, token_id: UUID, at: datetime) -> None:
        self._session.execute(update(ActionTokenModel).where(ActionTokenModel.id == token_id).values(used_at=at))

    def invalidate_for_user(self, user_id: UUID, purpose: TokenPurpose, at: datetime) -> None:
        self._session.execute(
            update(ActionTokenModel)
            .where(
                ActionTokenModel.user_id == user_id,
                ActionTokenModel.purpose == purpose.value,
                ActionTokenModel.used_at.is_(None),
            )
            .values(used_at=at)
        )


class SqlAlchemyRefreshSessionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, refresh: RefreshSession) -> None:
        self._session.add(
            RefreshSessionModel(
                id=refresh.id,
                user_id=refresh.user_id,
                family_id=refresh.family_id,
                token_hash=refresh.token_hash,
                expires_at=refresh.expires_at,
                revoked_at=refresh.revoked_at,
                user_agent=refresh.user_agent,
            )
        )

    def get_by_hash(self, token_hash: str) -> RefreshSession | None:
        row = self._session.scalar(select(RefreshSessionModel).where(RefreshSessionModel.token_hash == token_hash))
        if row is None:
            return None
        return RefreshSession(
            id=row.id,
            user_id=row.user_id,
            family_id=row.family_id,
            token_hash=row.token_hash,
            expires_at=row.expires_at,
            revoked_at=row.revoked_at,
            user_agent=row.user_agent,
        )

    def _revoke_where(self, *conditions, at: datetime) -> None:
        self._session.execute(
            update(RefreshSessionModel)
            .where(*conditions, RefreshSessionModel.revoked_at.is_(None))
            .values(revoked_at=at)
        )

    def revoke(self, session_id: UUID, at: datetime) -> None:
        self._revoke_where(RefreshSessionModel.id == session_id, at=at)

    def revoke_family(self, family_id: UUID, at: datetime) -> None:
        self._revoke_where(RefreshSessionModel.family_id == family_id, at=at)

    def revoke_all_for_user(self, user_id: UUID, at: datetime) -> None:
        self._revoke_where(RefreshSessionModel.user_id == user_id, at=at)
