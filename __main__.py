import asyncio
from options.database.db import init_db
from options.queue.tasks import update_stock_prices, update_stock_tickers
from options.queries import get_all_stocks
from options.log import log_factory

logger = log_factory(name=f"{__name__}")


def main(): ...


if __name__ == "__main__":
    init_db()
    main()
