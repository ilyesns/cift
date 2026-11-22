from fastapi import APIRouter, Response, status

from app.api.deps import AccountServiceDep, CurrentUser
from app.api.v1.schemas.users import ChangePasswordIn, UpdateProfileIn, UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def read_me(user: CurrentUser) -> UserOut:
    return UserOut.from_domain(user)


@router.patch("/me", response_model=UserOut)
def update_me(body: UpdateProfileIn, user: CurrentUser, service: AccountServiceDep) -> UserOut:
    updated = service.update_profile(
        user.id,
        full_name=body.full_name,
        preferred_locale=body.preferred_locale,
        preferred_city=body.preferred_city,
    )
    return UserOut.from_domain(updated)


@router.post("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(body: ChangePasswordIn, user: CurrentUser, service: AccountServiceDep) -> Response:
    service.change_password(user.id, current=body.current_password, new=body.new_password)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
