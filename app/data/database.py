from sqlalchemy import create_engine

from sqlalchemy.orm import Session, sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://myuser:mypassword@0.0.0.0:5432/mydb"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    # SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} # for sqlite
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine,expire_on_commit=False)



def get_session() -> Session:
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine,expire_on_commit=False)
    return session()
