from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from data import crud, models, schemas
from data.schemas import Token
from utils import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    get_dp,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authenticate"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post("/token", tags=["Authenticate"])
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_dp),
) -> Token:
    user = authenticate_user(
        db=db, username=form_data.username, password=form_data.password
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


@router.post("/acount", response_model=schemas.User)
def create_new_account(user: schemas.UserCreate, db: Session = Depends(get_dp)):
    db_user = crud.get_user_by_username(db=db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User name already registered.",
        )
    return crud.create_user(db=db, user=user)
