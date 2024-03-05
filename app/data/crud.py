from sqlalchemy.orm import Session
from . import models, schemas


from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> models.User:
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db_avatar = models.UserAvatar(
        filename="default_avatar.png", owner=db_user, contents=b""
    )
    
    db.add(db_user)
    db.add(db_avatar)
    db.commit()
    db.refresh(db_user)
    db_user.avatar = db_avatar
    return db_user


# Conversation


def get_conversations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Conversation).offset(skip).limit(limit).all()


def create_user_conversation(
    db: Session, conversation: schemas.ConversationCreate, user_id: int
):
    db_item = models.Conversation(**conversation.model_dump(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


# Message


def create_conversation_message(
    db: Session, message: schemas.MessageCreate, conversation_id: int
):
    db_item = models.Message(**message.model_dump(), conversation_id=conversation_id)
    conversation = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if conversation.title == "":
        conversation.title = message.content
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


# Upload File


def upload_file(db: Session, file: schemas.CreateUploadAvatar) -> models.UserAvatar:
    db_file = models.UserAvatar(
        filename=file.filename, contents=file.contents, owner_id=file.user_id
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file
