import subprocess
from typing import Union,Annotated
from fastapi import FastAPI, Depends, HTTPException,status
from datetime import datetime
from fastapi.responses import StreamingResponse
from openai import OpenAI, AsyncOpenAI
from model.models import Token, TokenData, User, UserInDb
from utils import  sendQuestion
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext


# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def bash_read():
    child = subprocess.Popen("openssl rand -hex 32".split(), stdout=subprocess.PIPE)
    bytes_string = child.communicate()[0]  # stdout content
    return bytes_string.decode()

SECRET_KEY = bash_read()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 20
pwd_context = CryptContext(schemes=["bcrypt"],deprecated = "auto")   

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password,hashed_password)
def get_password_hashed(password):
    return pwd_context.hash(password)

def authenticate_user(fake_db,username:str, password: str):
    user = get_user(fake_db,username=username)
    if not user:
        return False
    if not verify_password(password,user.hashed_password):
        return False
    return user

def create_access_token(data:dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expires = datetime.now(timezone.utc) + expires_delta
    else:
        expires = datetime.now() +  timedelta(minutes=15)
    to_encode.update({"exp":expires})
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt
    
def get_user(db,username: str):
    if username in db:
        user_dict = db[username]
        return UserInDb(**user_dict)
    
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Admin",
        "email": "admin@example.com",
        "hashed_password": get_password_hashed(password="secret"),
        "disabled": False,
    }
}


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credential_exception = HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= "Invalid authentication credentials",
            headers={"WWW-Authenticate":"Bearer"}
        )
    try:
        payload = jwt.decode(token = token, key= SECRET_KEY, algorithms= [ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
        token_data  = TokenData(username=username)
    except JWTError:
        raise credential_exception
    
    user = get_user(fake_users_db,username=token_data.username)
    if user is None:
        raise credential_exception
    return user

async def get_current_active_user(current_user: Annotated[User,Depends(get_current_user)]) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400,detail="Inactive user")
    return current_user



@app.post("/token",tags=["Authenticate"])
async def login(form_data: Annotated[OAuth2PasswordRequestForm,Depends()]) -> Token:
    print(form_data)
    user = authenticate_user(fake_db=fake_users_db,username= form_data.username,password=form_data.password)
    if not user:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= "Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username},expires_delta=access_token_expires)
    return Token(access_token=access_token,token_type="bearer")

@app.get("/users/me",tags=["Profile"],response_model=User)
async def read_users_me(current_users: Annotated[User,Depends(get_current_active_user)]):
    return current_users

@app.get("/chat",tags=["CHAT"])
async def chat_stream(message: str,token: Annotated[str, Depends(get_current_active_user)]):
    return StreamingResponse(sendQuestion(message=message),media_type="text/event-stream")

@app.get("/user/me/items/")
async def read_own_items(current_user: Annotated[User,Depends(get_current_active_user)]):
    return [{"items":"Foo","owner":current_user.username}]