from typing import TypeVar
from pydantic import BaseModel

T = TypeVar("T")

# class Response(BaseModel,Generic[T]):
#     status_code: int
#     message: str
#     data: Optional[T] = None

# class MessageResponse(BaseModel):
#     event_id: int
#     data: str
#     is_last_event: bool
#     def toJson(self):
#         return json.dumps({"event_id": self.event_id,"data": self.data,"is_last_event":self.is_last_event})
    
