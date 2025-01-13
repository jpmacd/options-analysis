from os import getenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData
from .models import Base


DATABASE_URL = getenv("DATABASE_URL", "default")

engine = create_async_engine(DATABASE_URL, echo=False, future=True)

session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

metadata = MetaData()


async def get_db_session():
    async with session_factory() as s:
        yield s


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
