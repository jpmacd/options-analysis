from os import getenv
from polygon import RESTClient
from options.log import log_factory
from typing import Optional
from options.utils import convert_timestamp

logger = log_factory(name=f"{__name__}")


client = RESTClient(api_key=getenv(f"API_KEY"))


def get_all_stocks():
    try:
        r = client.list_tickers(market="stocks", active=True, limit="1000")
        unique_results = {(x.ticker, x.name) for x in r}
        return [{"ticker": ticker, "name": name} for ticker, name in unique_results]
    except Exception as e:
        logger.exception(f"{e.__class__.__name__}")
        return []


def get_call_options(ticker: Optional[str] = None) -> list:
    results: list = []
    try:
        r = client.list_options_contracts(
            underlying_ticker=ticker,
            contract_type="call",
            limit="5",
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
        logger.info(f"Retrieved {len(results)} options for ${ticker}")
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
        logger.info(f"Requesting stock quote for {ticker}")
        results.append(
            {
                "underlying_last_trade_price": r.price,
                "underlying_ticker": ticker,
            }
        )
        logger.info(f"Quote: {results}")
    except Exception as e:
        logger.exception(f"{e.__class__.__name__}")
    finally:
        return results


def get_options_quote(ticker: str):
    results: list = []
    try:
        r = client.get_last_quote(
            ticker=ticker,
        )
        logger.info(f"Requesting option quote for {ticker}")
        results.append(
            {
                "ticker": r.ticker,
                "ask_price": r.ask_price,
                "ask_size": r.ask_size,
                "timestamp": convert_timestamp(r.sip_timestamp),
            }
        )
        logger.info(f"Quote: {results}")
    except Exception as e:
        logger.exception(f"{e.__class__.__name__}")
    finally:
        return results
