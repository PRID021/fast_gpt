from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from http import HTTPStatus
from typing import Any, Generic, TypeVar,Optional
from fastapi.responses import StreamingResponse
import asyncio
import json
from openai import OpenAI, AsyncOpenAI
import os
import asyncio
from utils import async_client, sendQuestion
from fastapi.middleware.cors import CORSMiddleware

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

T = TypeVar("T")

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Response(BaseModel,Generic[T]):
    status_code: int
    message: str
    data: Optional[T] = None

class MessageResponse(BaseModel):
    event_id: int
    data: str
    is_last_event: bool
    def toJson(self):
        return json.dumps({"event_id": self.event_id,"data": self.data,"is_last_event":self.is_last_event})
    
@app.get("/")
def hello():
    return "hello"

@app.get("/chat",tags=["CHAT"])
async def chat_stream(message: str):
    return StreamingResponse(sendQuestion(message=message),media_type="application/x-ndjson")