from options.database.db import engine
from options.database.models import Base


async def init_db():
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)
