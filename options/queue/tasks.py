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
from celery import chain
import time

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
    if not data:
        logger.warning(f"No quote data available for ticker: {t}")
        return

    # Sort data by ticker (if needed)
    data = sorted(data, key=lambda x: x.get("option_id"))

    for entry in data:
        # Fetch the option ID
        option_id_result = execution_handler(
            select(Options.id).where(Options.ticker == entry.get("option_id"))
        )
        if not option_id_result:
            logger.warning(
                f"No matching Options entry found for ticker: {entry.get('option_id')}"
            )
            continue

        # Assign `option_id` for the quote
        entry["option_id"] = option_id_result[0][0]

        # Insert or update the quote
        try:
            query = (
                pginsert(OptionsQuote)
                .values(entry)
                .on_conflict_do_update(
                    index_elements=["option_id", "timestamp"],
                    set_={
                        "ask_price": entry["ask_price"],
                        "ask_size": entry["ask_size"],
                    },
                )
            )
            execution_handler(query)
            logger.info(
                f"Quote successfully updated for ticker: {entry.get('option_id')}"
            )
        except Exception as e:
            logger.exception(
                f"Failed to update quote for ticker {entry.get('option_id')}: {e}"
            )


@app.task
def spawn_update_options_quote():
    tickers = execution_handler(select(Options.ticker).limit(1))
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
        update_stock_quote.apply_async(args=[ticker])
    logger.info(f"queued {tasks} tasks")


@app.task
def update_stock_tickers_and_call_options():
    # Run `update_stock_tickers` and ensure it completes first
    update_result = app.send_task("options.queue.tasks.update_stock_tickers")

    # Wait for the first task to complete
    while not update_result.ready():
        time.sleep(1)

    # If `update_stock_tickers` is successful, proceed to `spawn_update_call_options`
    if update_result.successful():
        app.send_task("options.queue.tasks.spawn_update_call_options")
    else:
        raise RuntimeError(
            "Failed to update stock tickers; skipping update call options."
        )


@app.on_after_configure.connect
def run_on_startup(sender, **kwargs):
    # Trigger the orchestrated tasks at startup
    app.send_task("options.queue.tasks.update_stock_tickers_and_call_options")
