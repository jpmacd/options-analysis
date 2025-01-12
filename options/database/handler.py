from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from options.database.db import get_db_session


async def query_handler(query):
    engine = create_async_engine(engine_url, echo=True, future=True)
    s = get_db_session()

    try:
        async with s as s:
            result = await s.execute(query)
            return result.scalars().all()

    finally:
        await engine.dispose()
