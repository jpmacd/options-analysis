from urllib.parse import urlencode, urlparse, parse_qs
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from options.database.db import get_db_session
from options.database.models import Stocks
from options.database.handler import query_handler
from options.log import log_factory
from os import getenv
import asyncio
import httpx
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Constants
API_KEY = getenv("API_KEY")
BASE_URL = "https://api.polygon.io"

if not API_KEY:
    raise ValueError("API key is not set. Please provide a valid API key.")

logger = log_factory(name=f"{__name__}")
logger.setLevel("INFO")


async def save_or_update(session: AsyncSession, model, unique_field: str, data: dict):
    existing_entity_query = select(model).where(
        getattr(model, unique_field) == data[unique_field]
    )
    existing_entity = await query_handler(existing_entity_query)

    if not existing_entity:
        new_entity = model(**data)
        session.add(new_entity)
    else:
        existing_entity = existing_entity[0]
        for key, value in data.items():
            setattr(existing_entity, key, value)

    await session.commit()


async def save_stocks_to_db(stocks_data):
    async for session in get_db_session():
        for stock in stocks_data:
            stock_data = {
                "ticker": stock["ticker"],
                "price": stock.get("price", None),
            }
            await save_or_update(session, Stocks, "ticker", stock_data)


class PolygonAPIHandler:
    def __init__(self, api_key):
        self.api_key = api_key

    def build_url(self, endpoint, params=None):
        if params is None:
            params = {}
        params["apiKey"] = self.api_key
        query_string = urlencode(params)
        url = f"{BASE_URL}{endpoint}?{query_string}"
        return url

    def ensure_api_key_in_url(self, url):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        if "apiKey" not in query_params:
            query_params["apiKey"] = self.api_key

        new_query_string = urlencode(query_params, doseq=True)
        return parsed_url._replace(query=new_query_string).geturl()

    async def send_request(self, url):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                logger.warning(f"GET {url}")

                if response.status_code != 200:
                    logger.error(f"status {response.status_code}")
                return response.json()
        except httpx.RequestError as e:
            return {"error": f"Request failed: {str(e)}"}

    async def get_data(self, endpoint, params=None):
        all_data = []
        next_url = self.build_url(endpoint, params)

        while next_url:
            next_url = self.ensure_api_key_in_url(next_url)

            response = await self.send_request(next_url)
            logger.info(f"response: {response}")

            if "error" in response:
                logger.error(f"{response['error']}")
                break

            results = response.get("results")
            if not results:
                return response
            if results:
                all_data.append(results)
            next_url = response.get("next_url")
            if not next_url:
                logger.info("No more pages to fetch.")
            return all_data


async def download_all_stock_tickers():
    handler = PolygonAPIHandler(API_KEY)

    stocks_data = await handler.get_data(
        endpoint="/v3/reference/tickers",
        params={
            "market": "stocks",
            "active": "true",
            "limit": "1000",
        },
    )

    if not stocks_data:
        logger.info("No stocks data retrieved.")
        return None

    await save_stocks_to_db(stocks_data)
    logger.info(f"Saved {len(stocks_data)} stocks to the database.")

    return len(stocks_data)


async def download_stock_price(ticker):
    handler = PolygonAPIHandler(API_KEY)

    # Log ticker and its type to debug any issues
    logger.info(f"Ticker: {ticker} (type: {type(ticker)})")

    # Fetch stock price data from Polygon API
    stock_price_data = await handler.get_data(
        endpoint=f"/v2/last/trade/{ticker}",
        params={},
    )
    logger.info(f"stock_price_data {stock_price_data}")
    if not stock_price_data:
        logger.info(f"No price data for {ticker}")
        return

    logger.info(f"Fetched stock price data for {ticker}")

    if isinstance(stock_price_data, list) and stock_price_data:
        stock_data_dict = stock_price_data[0]
        logger.info(f"{type(stock_data_dict)}")
        price = stock_data_dict.get("p")
        updated = stock_data_dict.get("f")

    # Prepare data to save
    stock_data = {"ticker": ticker, "price": price, "updated": updated}

    # Save stock data to database
    await save_stocks_to_db([stock_data])
    logger.info(f"Saved current price for {ticker}: {ask_price}")
