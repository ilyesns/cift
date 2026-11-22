from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query, Request, Response

from app.api.deps import PrayerTimesServiceDep
from app.api.v1.schemas.prayer import CityOut, TimetableOut
from app.domain.i18n import locale_from_accept_language

router = APIRouter(prefix="/prayer-times", tags=["prayer times"])

# Times change at most once a day; let browsers and proxies reuse answers for 5 minutes
CACHE = "public, max-age=300"


def _locale(request: Request) -> str:
    return locale_from_accept_language(request.headers.get("accept-language"))


# Declared before "/{city}" so "cities" isn't read as a city slug
@router.get("/cities", response_model=list[CityOut])
def list_cities(request: Request, response: Response, service: PrayerTimesServiceDep) -> list[CityOut]:
    response.headers["Cache-Control"] = CACHE
    return [CityOut.from_domain(c, _locale(request)) for c in service.cities()]


@router.get("/{city}", response_model=TimetableOut)
def get_prayer_times(
    city: str,
    request: Request,
    response: Response,
    service: PrayerTimesServiceDep,
    start: Annotated[date | None, Query(alias="from", description="First day, default today")] = None,
    end: Annotated[date | None, Query(alias="to", description="Last day, default = from")] = None,
) -> TimetableOut:
    response.headers["Cache-Control"] = CACHE
    return TimetableOut.from_domain(service.timetable(city, start, end), _locale(request))
