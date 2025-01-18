from options.queue.celery import app
from options.database.handler import execution_handler
from options.database.db import get_db_session
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
from celery import chain
import time
from datetime import datetime


logger = log_factory(f"{__name__}")

LIMIT = 999999


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


from datetime import datetime


@app.task
def update_options_quote(t: str):
    data = get_options_quote(ticker=t)
    if not data:
        logger.warning(f"No quote data available for ticker: {t}")
        return

    option_id_result = execution_handler(select(Options.id).where(Options.ticker == t))
    if not option_id_result:
        logger.warning(f"No matching Options entry found for ticker: {t}")
        return

    option_id = option_id_result[0][0]

    for entry in data:
        quote = {
            "option_id": option_id,
            "timestamp": entry["timestamp"],  # Use the timestamp as-is
            "ask_price": entry["ask_price"],
            "ask_size": entry["ask_size"],
        }

        query = (
            pginsert(OptionsQuote)
            .values(**quote)
            .on_conflict_do_update(
                index_elements=["option_id"],  # Unique constraint columns
                set_={
                    "ask_price": quote["ask_price"],
                    "ask_size": quote["ask_size"],
                    "timestamp": entry["timestamp"],
                },
            )
        )

        try:
            execution_handler(query)
            logger.info(
                f"Processed quote for option_id: {option_id}, timestamp: {entry['timestamp']}"
            )
        except Exception as e:
            logger.exception(f"Failed to update quote for option_id {option_id}: {e}")


@app.task
def update_stocks_quote(t: str):
    data = get_stock_quote(ticker=t)
    if not data:
        logger.warning(f"No quote data available for ticker: {t}")
        return

    stock_id_result = execution_handler(select(Stocks.id).where(Stocks.ticker == t))
    if not stock_id_result:
        logger.warning(f"No matching Stock entry found for ticker: {t}")
        return

    stock_id = stock_id_result[0][0]

    for entry in data:
        try:
            query = (
                pginsert(StocksQuote)
                .values(
                    {
                        "stock_id": stock_id,
                        "timestamp": entry["timestamp"],
                        "price": entry["price"],
                    }
                )
                .on_conflict_do_update(
                    index_elements=[
                        "stock_id",
                    ],  # Unique constraint columns
                    set_={
                        "price": entry["price"],
                        "timestamp": entry["timestamp"],
                    },  # Only update the price
                )
            )
            execution_handler(query)
            logger.info(
                f"Processed quote for stock_id: {stock_id}, timestamp: {entry['timestamp']}"
            )
        except Exception as e:
            logger.exception(f"Failed to process quote for stock_id {stock_id}: {e}")


@app.task
def spawn_update_options_quote():
    tickers = execution_handler(select(Options.ticker).limit(LIMIT))
    for (ticker,) in tickers:
        update_options_quote.apply_async(args=[ticker])


@app.task
def spawn_update_stocks_quote():
    tickers = execution_handler(select(Stocks.ticker).limit(LIMIT))
    for (ticker,) in tickers:
        update_stocks_quote.apply_async(args=[ticker])


@app.task
def spawn_update_call_options():
    tickers = execution_handler(select(Stocks.ticker).limit(LIMIT))
    for (ticker,) in tickers:
        update_call_options.apply_async(args=[ticker])


@app.task
def update_stock_tickers_and_call_options():
    try:
        result = app.send_task("options.queue.tasks.update_stock_tickers")
        task_result = result.get(timeout=300)
        if result.state == "SUCCESS":
            app.send_task("options.queue.tasks.spawn_update_call_options")
        else:
            raise RuntimeError(
                f"Task update_stock_tickers failed with state: {result.state}. Skipping call options update."
            )
    except Exception as e:
        raise RuntimeError(f"Error during task execution: {e}")


# @app.on_after_finalize.connect
# def run_on_startup(sender, **kwargs):
#     app.send_task("options.queue.tasks.update_stock_tickers_and_call_options")
