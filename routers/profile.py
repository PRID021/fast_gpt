from typing import Annotated

from fastapi import APIRouter, Depends, status

from data import models, schemas
from utils import get_current_active_user

router = APIRouter(
    prefix="/user",
    tags=["Profile"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get("/me", tags=["Profile"], response_model=schemas.User)
async def read_users_me(
    current_users: Annotated[models.User, Depends(get_current_active_user)]
):
    return current_users


@router.get("/me/items")
async def read_own_items(
    current_user: Annotated[models.User, Depends(get_current_active_user)]
):
    return [{"items": "Foo", "owner": current_user.username}]
