import pg8000
import sqlalchemy
from google.cloud.sql.connector import Connector, IPTypes
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ..setting import settings

SQLALCHEMY_DATABASE_URL = settings.LOCAL_DB_URI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)


def get_session() -> Session:
    session = sessionmaker(
        autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
    )
    return session()
