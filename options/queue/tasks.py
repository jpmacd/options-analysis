from options.queue.celery import app
from options.database.handler import execution_handler
from options.datasource import (
    get_all_stocks,
    get_call_options,
    get_options_quote,
    get_stock_quote,
)
from options.log import log_factory
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pginsert
from options.database.models import Stocks, Options, StocksQuote, OptionsQuote

logger = log_factory(f"{__name__}")


@app.task
def update_stock_tickers():
    data = get_all_stocks()
    if data:
        query = pginsert(Stocks).values(data).on_conflict_do_nothing()
        execution_handler(query)


@app.task
def update_call_options(t: str):
    data = get_call_options(ticker=t)
    for entry in data:
        query = (
            pginsert(Options)
            .values(entry)
            .on_conflict_do_update(
                index_elements=["ticker"], set_={key: entry[key] for key in entry}
            )
        )
        execution_handler(query)


@app.task
def spawn_update_call_options():
    tickers = execution_handler(select(Stocks.ticker))
    for (ticker,) in tickers:
        update_call_options.apply_async(args=[ticker])


@app.task
def update_options_quote(t: str):
    data = get_options_quote(ticker=t)
    data = sorted(data, key=lambda x: x.get("ticker"))
    for entry in data:
        option_id = execution_handler(
            select(Options.id).where(Options.ticker == entry.get("ticker"))
        )
        if option_id:
            entry["option_id"] = option_id[0][0]
            entry["ask_price"] = entry.pop("ask_price")
            query = pginsert(OptionsQuote).values(entry).on_conflict_do_nothing()
            execution_handler(query)


@app.task
def spawn_update_options_quote():
    tickers = execution_handler(select(Options.ticker))
    for (ticker,) in tickers:
        update_options_quote.apply_async(args=[ticker])


@app.task
def update_stock_quote(t: str):
    data = get_stock_quote(ticker=t)
    stock_id = execution_handler(select(Stocks.id).where(Stocks.ticker == t))
    if stock_id:
        for entry in data:
            entry["stock_id"] = stock_id[0][0]
            entry["price"] = entry.pop("price")
            query = pginsert(StocksQuote).values(entry).on_conflict_do_nothing()
            execution_handler(query)


@app.task
def spawn_update_stock_quote():
    tasks = 0
    tickers = execution_handler(select(Stocks.ticker))
    for (ticker,) in tickers:
        tasks += 1
        update_stock_quote.apply_async(args=[ticker])
    logger.info(f"queued {tasks} tasks")
