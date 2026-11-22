from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query

from app.api.deps import AccountServiceDep, AdminUser
from app.api.v1.schemas.users import SetRolesIn, UserOut, UserPageOut

router = APIRouter(prefix="/admin/users", tags=["admin"])


@router.get("", response_model=UserPageOut)
def list_users(
    _: AdminUser,
    service: AccountServiceDep,
    q: Annotated[str | None, Query(max_length=100)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> UserPageOut:
    users, total = service.search_users(query=q, page=page, page_size=page_size)
    return UserPageOut(items=[UserOut.from_domain(u) for u in users], total=total, page=page, page_size=page_size)


@router.put("/{user_id}/roles", response_model=UserOut)
def set_roles(user_id: UUID, body: SetRolesIn, actor: AdminUser, service: AccountServiceDep) -> UserOut:
    return UserOut.from_domain(service.set_roles(actor, user_id, frozenset(body.roles)))
