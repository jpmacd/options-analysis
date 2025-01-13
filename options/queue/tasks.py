from options.queue.celery import app
from options.database.handler import query_handler
from options.polygon import download_all_stock_tickers, download_stock_price
import asyncio
from options.log import log_factory
from sqlalchemy.future import select
from options.database.models import Stocks

logger = log_factory(f"{__name__}")


@app.task
def update_stock_tickers():
    try:
        result = asyncio.run(download_all_stock_tickers())
        if result is None:
            logger.error("No data was retrieved from Polygon API.")
        else:
            logger.info(f"Successfully retrieved and saved {result} stock tickers.")
        return result
    except Exception as e:
        logger.error(f"Task failed with error: {str(e)}")
        return None


@app.task
def update_stock_prices():
    try:

        async def fetch_prices():
            all_tickers = await query_handler(query=select(Stocks.ticker))
            for ticker in all_tickers:
                await download_stock_price(ticker=ticker)

        asyncio.run(fetch_prices())
    except Exception as e:
        logger.error(f"Task failed with error: {str(e)}")
