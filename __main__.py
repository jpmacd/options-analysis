from options.routine.stocks import get_all_stocks
from options.database.db import init_db
from options.queue.tasks import add
import asyncio


async def main():
    await init_db()
    stocks = await get_all_stocks()
    print(len(stocks))
    print(type(stocks))
    print(stocks)
    r = add.apply_async((1, 2))
    print(r)
    print(r.get())


asyncio.run(main())
