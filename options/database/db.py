from os import getenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData
from sqlalchemy.future import select  # For async query generation


# Configure the database URL (PostgreSQL example)
DATABASE_URL = getenv("DATABASE_URL", "default")

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Create sessionmaker for AsyncSession (factory for creating async sessions)
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,  # This specifies that we want to use AsyncSession
    expire_on_commit=False,  # Prevent session objects from expiring after commit
)

metadata = MetaData()


async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
