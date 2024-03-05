from sqlalchemy import create_engine

from sqlalchemy.orm import Session, sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://myuser:mypassword@postgres:5432/gptservice"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    # SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} # for sqlite
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
