from options.routine.stocks import result
from options.database.create import init_db
import asyncio


asyncio.run(init_db())


print(result.get())
