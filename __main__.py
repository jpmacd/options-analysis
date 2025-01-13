import asyncio
from options.database.db import init_db
from options.queue.tasks import update_stock_prices, update_stock_tickers
from options.queries import get_all_stocks
from options.log import log_factory

logger = log_factory(name=f"{__name__}")
logger.setLevel("INFO")


async def main():
    await init_db()

    # task_result = update_stock_tickers.apply_async()
    # logger.info(f"Task enqueued with ID: {task_result.id}")
    # await wait_for_task_result(task_result)

    task_result = update_stock_prices.apply_async()
    await wait_for_task_result(task_result)


async def wait_for_task_result(task_result):
    # Poll for the result in an asynchronous manner
    while not task_result.ready():
        logger.info("Waiting for the task to complete...")
        await asyncio.sleep(1)  # Non-blocking wait (sleep for 1 second)

    logger.info(f"Task {task_result.id} completed, retrieving result...")

    # Offload the blocking get() call into a separate thread
    try:
        result = await asyncio.to_thread(task_result.get)
        logger.info(f"Task result: {result}")
    except Exception as e:
        logger.error(f"Error retrieving task result: {e}")


if __name__ == "__main__":
    asyncio.run(main())  # Run the main async function
