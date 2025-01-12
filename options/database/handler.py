from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from options.database.db import get_db_session, engine


async def query_handler(query):

    try:
        async for s in get_db_session():
            result = await s.execute(query)
            return result.scalars().all()

    finally:
        await s.aclose()
