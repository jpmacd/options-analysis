from os import getenv
from polygon import RESTClient
from options.log import log_factory
from typing import Optional

logger = log_factory(name=f"{__name__}")


client = RESTClient(api_key=getenv(f"API_KEY"))


def get_all_stocks():
    try:
        results = []
        r = client.list_tickers(market="stocks", active=True, limit="1000")
        results.extend([x.ticker for x in r])
    except Exception as e:
        logger.exception(f"{e.__class__.__name__}")
    finally:
        return results


def get_call_options(ticker: Optional[str] = None) -> list:
    try:
        results = []
        r = client.list_options_contracts(
            contract_type="call", limit="1000", underlying_ticker=ticker, expired=False
        )
        results.extend(r)
    except Exception as e:
        logger.exception(f"{e.__class__.__name__}")
    finally:
        return results


def get_stock_last_trade(ticker: str):
    try:
        return client.get_last_trade(
            ticker=ticker,
        )
    except Exception as e:
        logger.exception(f"{e.__class__.__name__}")


def get_options_quote(ticker: str):
    try:
        return client.get_last_quote(
            ticker=ticker,
        )
    except Exception as e:
        logger.exception(f"{e.__class__.__name__}")
