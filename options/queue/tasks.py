from options.queue.celery import app
from options.database.handler import execution_handler
from options.datasource import (
    get_all_stocks,
    get_call_options,
    get_options_quote,
    get_stock_quote,
)
import asyncio
from options.log import log_factory
from sqlalchemy import select, insert, update
from options.database.models import Stocks, Options
from sqlalchemy.dialects.postgresql import insert as pginsert


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
    tickers = execution_handler(select(Stocks.ticker).limit(2))
    for ticker in tickers:
        update_call_options.apply_async(args=[ticker])


@app.task
def update_options_quote(t: str):
    data = get_options_quote(ticker=t)
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
def spawn_update_options_quote():
    tickers = execution_handler(select(Options.ticker).limit(2))
    for ticker in tickers:
        logger.info(f"Spawning task to update options quote {ticker}")
        update_options_quote.apply_async(args=[ticker])


@app.task
def update_stock_quote(t: str):
    data = get_stock_quote(ticker=t)
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
def spawn_update_stock_quote():
    tickers = execution_handler(select(Options.ticker).limit(2))
    for ticker in tickers:
        logger.info(f"Spawning task to update stock quote {ticker}")
        update_stock_quote.apply_async(args=[ticker])
