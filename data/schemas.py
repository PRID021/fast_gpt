from typing import Optional

from pydantic import BaseModel, Field

# Upload file


class UploadAvatarBase(BaseModel):
    filename: str
    contents: bytes


class CreateUploadAvatar(UploadAvatarBase):
    user_id: int


class UploadAvatar(UploadAvatarBase):
    id: int

    class Config:
        orm_mode = True


# Token


class TokenData(BaseModel):
    username: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


# Message
class MessageBase(BaseModel):
    pass


class MessageCreate(MessageBase):
    content: str


class Message(MessageBase):
    id: int
    content: str
    conversation_id: int

    class Config:
        orm_mode = True


class ConversationBase(BaseModel):
    pass


class ConversationCreate(ConversationBase):
    title: str


class Conversation(ConversationBase):
    id: int
    title: str
    messages: list[Message]

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    conversations: list[Conversation] = []
    disabled: bool
    avatar: Optional[UploadAvatar] = None

    class Config:
        orm_mode = True
