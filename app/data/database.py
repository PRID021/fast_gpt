from sqlalchemy import create_engine

from sqlalchemy.orm import Session, sessionmaker
from ..setting import settings

from google.cloud.sql.connector import Connector, IPTypes
import pg8000
import sqlalchemy


# def connect_with_connector() -> sqlalchemy.engine.base.Engine:
#     """
#     Initializes a connection pool for a Cloud SQL instance of Postgres.

#     Uses the Cloud SQL Python Connector package.
#     """
#     # Note: Saving credentials in environment variables is convenient, but not
#     # secure - consider a more secure solution such as
#     # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
#     # keep secrets safe.

#     instance_connection_name = settings.INSTANCE_CONNECTION_NAME  # e.g. 'project:region:instance'
#     db_user = settings.DB_USER  # e.g. 'my-db-user'
#     db_pass = settings.DB_PASS  # e.g. 'my-db-password'
#     db_name = settings.DB_NAME  # e.g. 'my-database'

#     ip_type = IPTypes.PRIVATE if settings.PRIVATE_IP else IPTypes.PUBLIC

#     # initialize Cloud SQL Python Connector object
#     connector = Connector()

#     def getconn() -> pg8000.dbapi.Connection:
#         conn: pg8000.dbapi.Connection = connector.connect(
#             instance_connection_name,
#             "pg8000",
#             user=db_user,
#             password=db_pass,
#             db=db_name,
#             ip_type=ip_type,
#         )
#         return conn

#     # The Cloud SQL Python Connector can be used with SQLAlchemy
#     # using the 'creator' argument to 'create_engine'
#     pool = sqlalchemy.create_engine(
#         "postgresql+pg8000://",
#         creator=getconn,
#         # ...
#     )
#     return pool
# engine = connect_with_connector()

# SQLALCHEMY_DATABASE_URL = settings.POSTGRES_DB_URI
# SQLALCHEMY_DATABASE_URL = "postgresql://myuser:mypassword@postgres:5432/gptservice"
SQLALCHEMY_DATABASE_URL = settings.DB_URI

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
