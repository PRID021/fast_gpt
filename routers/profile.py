
from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from model.models import Token, User
from utils import get_current_active_user


router = APIRouter(
    prefix="/user",
    tags= ["Profile"],
    responses = {status.HTTP_404_NOT_FOUND:{"description":"Not found"}}
)

@router.get("/me",tags=["Profile"],response_model=User)
async def read_users_me(current_users: Annotated[User,Depends(get_current_active_user)]):
    return current_users

@router.get("/me/items")
async def read_own_items(current_user: Annotated[User,Depends(get_current_active_user)]):
    return [{"items":"Foo","owner":current_user.username}]
