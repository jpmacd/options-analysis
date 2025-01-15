from os import getenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base

DATABASE_URL = getenv("DATABASE_URL", "default")

engine = create_engine(DATABASE_URL, echo=False, pool_size=100, max_overflow=25)

session_factory = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db_session():
    return session_factory()


def init_db():
    with engine.begin() as conn:
        Base.metadata.create_all(conn)
