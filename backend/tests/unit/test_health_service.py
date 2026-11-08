import pytest

from app.application.health_service import HealthService
from app.domain.exceptions import ServiceUnavailableError
from tests.fakes import FakeDatabaseProbe


def make_service(probe: FakeDatabaseProbe) -> HealthService:
    return HealthService(probe=probe, app_name="CIFT", environment="test")


def test_liveness_does_not_touch_the_database():
    probe = FakeDatabaseProbe()
    report = make_service(probe).liveness()

    assert report.status == "ok"
    assert report.app == "CIFT"
    assert probe.calls == 0


def test_database_up():
    probe = FakeDatabaseProbe(healthy=True)
    report = make_service(probe).database()

    assert report.database == "up"
    assert probe.calls == 1


def test_database_down_raises_domain_error():
    probe = FakeDatabaseProbe(healthy=False)

    with pytest.raises(ServiceUnavailableError) as exc_info:
        make_service(probe).database()

    assert exc_info.value.code == "database_unavailable"
    assert isinstance(exc_info.value.__cause__, ConnectionError)
