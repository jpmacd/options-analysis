from os import getenv
from polygon import RESTClient
from options.log import log_factory
from typing import Optional
from options.utils import convert_timestamp

logger = log_factory(name=f"{__name__}")

client = RESTClient(api_key=getenv(f"API_KEY"), num_pools=500)

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


def get_all_stocks():
    try:
        unique_results = set()
        for item in client.list_tickers(market="stocks", active=True, limit="1000"):
            if hasattr(item, "ticker") and hasattr(item, "name"):
                unique_results.add((item.ticker, item.name))
        return [{"ticker": ticker, "name": name} for ticker, name in unique_results]
    except Exception as e:
        logger.exception(f"Error in get_all_stocks: {e}")
        return []


def get_call_options(ticker: Optional[str] = None) -> list:
    results: list = []
    try:
        r = client.list_options_contracts(
            underlying_ticker=ticker,
            contract_type="call",
            limit="1000",
            expired=False,
        )
        results.extend(
            {
                "contract_type": x.contract_type,
                "underlying_ticker": x.underlying_ticker,
                "ticker": x.ticker,
                "expiration_date": x.expiration_date,
                "strike_price": x.strike_price,
                "shares_per_contract": x.shares_per_contract,
            }
            for x in r
        )
        logger.debug(f"Retrieved {len(results)} options for ${ticker}")
    except Exception as e:
        logger.exception(f"{e.__class__.__name__}")
    finally:
        return results


def get_stock_quote(ticker: str):
    results: list = []

    try:
        r = client.get_last_trade(
            ticker=ticker,
        )
        logger.debug(f"Requesting stock quote for {ticker}")
        results.append(
            {
                "price": r.price,
                "timestamp": convert_timestamp(r.sip_timestamp),
                "stock_id": ticker,
            }
        )
        logger.debug(f"Quote for {ticker}: {results}")
    except Exception as e:
        logger.exception(f"{e.__class__.__name__}")
    finally:
        return results


def get_options_quote(ticker: str):
    results: list = []
    try:
        logger.debug(f"Fetching quote for ticker: {ticker}")
        r = client.get_last_quote(ticker=ticker)
        results.append(
            {
                "ask_price": r.ask_price,
                "ask_size": r.ask_size,
                "timestamp": convert_timestamp(r.sip_timestamp),
                "option_id": ticker,
            }
        )
        logger.debug(f"Quote for {ticker}: {results}")

    except Exception as e:
        logger.exception(f"Error fetching options quote for ticker {ticker}: {e}")
    finally:
        return results
