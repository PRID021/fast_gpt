from sqlalchemy import Boolean,Column, ForeignKey,Integer,String
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    conversations = relationship("Conversation",back_populates="owner")
    
class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer,primary_key=True)
    title = Column(String,index=True)
    owner_id = Column(Integer,ForeignKey("users.id"))
    owner = relationship("User",back_populates="conversations")
    messages = relationship("Message",back_populates="conversation")
    

class Message(Base):
    __tablename__ ="messages"
    id = Column(Integer,primary_key=True)
    content = Column(String,index=True)
    conversation_id = Column(Integer,ForeignKey("conversations.id"))
    conversation = relationship("Conversation",back_populates="messages")