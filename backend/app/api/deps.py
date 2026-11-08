from typing import Annotated

from fastapi import Depends, Request

from app.application.health_service import HealthService
from app.core.config import Settings
from app.domain.ports.unit_of_work import UnitOfWork
from app.infrastructure.db.database import Database
from app.infrastructure.db.probe import SqlAlchemyDatabaseProbe
from app.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork


def get_app_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_database(request: Request) -> Database:
    return request.app.state.database


SettingsDep = Annotated[Settings, Depends(get_app_settings)]
DatabaseDep = Annotated[Database, Depends(get_database)]


def get_uow(database: DatabaseDep) -> UnitOfWork:
    return SqlAlchemyUnitOfWork(database.session_factory)


def get_health_service(database: DatabaseDep, settings: SettingsDep) -> HealthService:
    return HealthService(
        probe=SqlAlchemyDatabaseProbe(database.engine),
        app_name=settings.app_name,
        environment=settings.environment,
    )


UowDep = Annotated[UnitOfWork, Depends(get_uow)]
HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]