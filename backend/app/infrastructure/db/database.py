from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


class Database:
    def __init__(self, url: str, *, echo: bool = False) -> None:
        self.engine: Engine = create_engine(url, echo=echo, pool_pre_ping=True)
        self.session_factory: sessionmaker[Session] = sessionmaker(
            bind=self.engine, autoflush=False, expire_on_commit=False
        )

    def dispose(self) -> None:
        self.engine.dispose()