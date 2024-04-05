import os
import subprocess
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
# from openai import AsyncOpenAI, OpenAI
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from google.cloud import secretmanager
from .data import crud, models, schemas
from .data.database import SessionLocal
from  .setting import settings


OPENAI_API_KEY = settings.OPENAI_API_KEY
GEMINI_API_KEY = settings.GEMINI_API_KEY


# Dependency
def get_dp():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def bash_read():
    return "hoangsecret"
    child = subprocess.Popen("openssl rand -hex 32".split(), stdout=subprocess.PIPE)
    bytes_string = child.communicate()[0]  # stdout content
    return bytes_string.decode()


SECRET_KEY = bash_read()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 200


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hashed(password):
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expires = datetime.now(timezone.utc) + expires_delta
    else:
        expires = datetime.now() + timedelta(minutes=1005)
    to_encode.update({"exp": expires})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user(db: Session, username: str) -> models.User:
    db_user = crud.get_user_by_username(db=db, username=username)
    print(db_user)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"description": "Not exist user."},
        )
    return db_user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_dp)
) -> models.User:
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credential_exception

    user = get_user(db=db, username=token_data.username)
    if user is None:
        raise credential_exception
    return user


async def get_current_active_user(
    current_user: Annotated[models.User, Depends(get_current_user)]
) -> models.User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# client = OpenAI(
#     api_key=os.environ.get("OPENAI_API_KEY"),
# )

# async_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
