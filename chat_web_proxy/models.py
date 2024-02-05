import json
from typing import Generic, Optional, TypeVar
from pydantic import BaseModel


T = TypeVar("T")

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
    


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
    

class UserInDb(User):
    hashed_password: str
