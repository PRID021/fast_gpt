import enum
from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, LargeBinary, String,DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Sender(int, enum.Enum):
    HU = 0
    AI = 1


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    content = Column(String, index=True)
    sender = Column(Enum(Sender))
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    conversation = relationship("Conversation", back_populates="messages")
    created_at = Column(DateTime,nullable=True)


class UserAvatar(Base):
    __tablename__ = "user_avatar"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    contents = Column(LargeBinary)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="avatar")


class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", lazy="subquery")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    disabled = Column(Boolean, default=False)
    hashed_password = Column(String)
    conversations = relationship(
        "Conversation", back_populates="owner", lazy="subquery"
    )
    avatar = relationship("UserAvatar", back_populates="owner", uselist=False)
