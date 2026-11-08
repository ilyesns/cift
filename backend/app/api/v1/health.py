from fastapi import APIRouter

from app.api.deps import HealthServiceDep
from app.api.v1.schemas.health import DatabaseHealthOut, LivenessOut

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=LivenessOut)
def liveness(service: HealthServiceDep) -> LivenessOut:
    report = service.liveness()
    return LivenessOut(status=report.status, app=report.app, environment=report.environment)


@router.get("/db", response_model=DatabaseHealthOut)
def database(service: HealthServiceDep) -> DatabaseHealthOut:
    report = service.database()
    return DatabaseHealthOut(status=report.status, database=report.database)