from dataclasses import dataclass

from app.domain.exceptions import ServiceUnavailableError
from app.domain.ports.health import DatabaseProbe


@dataclass(frozen=True, slots=True)
class LivenessReport:
    status: str
    app: str
    environment: str


@dataclass(frozen=True, slots=True)
class DatabaseReport:
    status: str
    database: str


class HealthService:
    def __init__(self, probe: DatabaseProbe, app_name: str, environment: str) -> None:
        self._probe = probe
        self._app_name = app_name
        self._environment = environment

    def liveness(self) -> LivenessReport:
        return LivenessReport(status="ok", app=self._app_name, environment=self._environment)

    def database(self) -> DatabaseReport:
        try:
            self._probe.ping()
        except Exception as exc:
            raise ServiceUnavailableError(
                "Database is not reachable.", code="database_unavailable"
            ) from exc
        return DatabaseReport(status="ok", database="up")