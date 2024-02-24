from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from model.models import Token
from utils import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    fake_users_db,
)

router = APIRouter(
    prefix="/token",
    tags=["Authenticate"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post("", tags=["Authenticate"])
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    print(form_data)
    user = authenticate_user(
        fake_db=fake_users_db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
