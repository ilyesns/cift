"""Admin commands, run inside the API container:

docker compose exec api python -m app.cli create-superadmin you@example.com "Your Name"
"""

import argparse
import getpass
import sys
from datetime import UTC, datetime
from uuid import uuid4

from app.core.config import get_settings
from app.domain.users import Role, User, normalize_email
from app.infrastructure.db.database import Database
from app.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from app.infrastructure.security.passwords import Argon2PasswordHasher

SUPER_ROLES = frozenset({Role.MEMBER, Role.ADMIN, Role.SUPER_ADMIN})


def create_superadmin(email: str, full_name: str) -> None:
    password = getpass.getpass("Password (at least 8 characters): ")
    if len(password) < 8:
        sys.exit("Password too short.")
    if password != getpass.getpass("Repeat password: "):
        sys.exit("Passwords don't match.")

    email = normalize_email(email)
    now = datetime.now(UTC)
    hasher = Argon2PasswordHasher()
    database = Database(get_settings().database_url)
    try:
        with SqlAlchemyUnitOfWork(database.session_factory) as uow:
            existing = uow.users.get_by_email(email)
            if existing is not None:
                uow.users.set_roles(existing.id, existing.roles | SUPER_ROLES)
                uow.users.set_password_hash(existing.id, hasher.hash(password))
                if not existing.is_verified:
                    uow.users.mark_verified(existing.id, now)
                action = "Promoted"
            else:
                uow.users.add(
                    User(
                        id=uuid4(),
                        email=email,
                        password_hash=hasher.hash(password),
                        full_name=full_name,
                        preferred_locale="it",
                        preferred_city=None,
                        is_active=True,
                        email_verified_at=now,
                        created_at=now,
                        roles=SUPER_ROLES,
                    )
                )
                action = "Created"
            uow.commit()
    finally:
        database.dispose()
    print(f"{action} super admin {email}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m app.cli")
    commands = parser.add_subparsers(dest="command", required=True)

    superadmin = commands.add_parser("create-superadmin", help="Create or promote a super admin")
    superadmin.add_argument("email")
    superadmin.add_argument("full_name")

    args = parser.parse_args()
    if args.command == "create-superadmin":
        create_superadmin(args.email, args.full_name)


if __name__ == "__main__":
    main()
