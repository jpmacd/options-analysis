from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from options.database.handler import query_handler
from options.database.models import Stocks
from options.queue.tasks import add


async def get_all_stocks():
    stocks = await query_handler(query=select(Stocks))
    return stocks


result = add.delay(4, 5)
