from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .data import crud, models, schemas
from .data.database import engine
from .data.schemas import Token

# routers
from .routers import authenticate, chat, profile,gemi
from .utils import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    get_dp,
)

# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

models.Base.metadata.create_all(bind=engine)


app = FastAPI(title="Fast GPT", description="Hand-on practice python and openai")
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/token", tags=["Authenticate"])
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


app.include_router(authenticate.router)
app.include_router(profile.router)
app.include_router(chat.router)
app.include_router(gemi.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app=app, host="0.0.0.0", port=8080)
