from options.queue.celery import app
from options.database.handler import query_handler
from options.polygon import download_all_stock_tickers, download_stock_price
import asyncio
from options.log import log_factory
from sqlalchemy.future import select
from options.database.models import Stocks

logger = log_factory(f"{__name__}")


@app.task
def update_stock_tickers(): ...


@app.task
def update_stock_prices(): ...
