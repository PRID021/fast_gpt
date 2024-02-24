from sqlalchemy.orm import Session
from . import models, schemas
from utils import pwd_context

# User
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hash_password = pwd_context.hash(user.password)
    db_user =  models.User(username=user.username,hash_password=hash_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Conversation

def get_conversations(db: Session, skip:int = 0, limit:int =100):
    return db.query(models.Conversation).offset(skip).limit(limit).all()

def create_user_conversation(db: Session, conversation: schemas.ConversationCreate, user_id: int):
    db_item = models.Conversation(**conversation.dict(),owner_id = user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# Message

def create_conversation_message(db: Session, message: schemas.Message,conversation_id: int):
    db_item = models.Message(**message.dict(),conversation_id = conversation_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item