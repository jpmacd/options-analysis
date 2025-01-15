import time
import streamlit as st
import pandas as pd
from sqlalchemy.sql import select
from options.database.models import Options, OptionsQuote, Stocks, StocksQuote
from options.log import log_factory
from options.database.handler import execution_handler
from options.utils import get_task_queue_status

logger = log_factory(f"{__name__}")


def fetch_options_data():
    query = (
        select(
            Options.ticker,
            Options.underlying_ticker,
            Options.strike_price,
            Options.contract_type,
            Options.shares_per_contract,
            Options.expiration_date,
            Options.delta,
            OptionsQuote.ask_price,
            OptionsQuote.ask_size,
            OptionsQuote.timestamp.label("option_timestamp"),
            StocksQuote.price.label("stock_price"),
            StocksQuote.timestamp.label("stock_timestamp"),
        )
        .join(OptionsQuote, Options.id == OptionsQuote.option_id, isouter=True)
        .join(Stocks, Options.underlying_ticker == Stocks.ticker, isouter=True)
        .join(StocksQuote, Stocks.id == StocksQuote.stock_id, isouter=True)
    )
    result = execution_handler(query)
    return result if result else []


def calculate_fields(data):
    df = pd.DataFrame(
        data,
        columns=[
            "ticker",
            "underlying_ticker",
            "strike_price",
            "contract_type",
            "shares_per_contract",
            "expiration_date",
            "delta",
            "ask_price",
            "ask_size",
            "option_timestamp",
            "stock_price",
            "stock_timestamp",
        ],
    )
    if df.empty:
        return df
    df["option_price"] = df["ask_price"].fillna(0) * 100
    df["option_position_size"] = df["ask_size"].fillna(0) * df["option_price"]
    df["execution_cost"] = (
        df["strike_price"].fillna(0) * df["shares_per_contract"].fillna(0)
    ) * 100
    df["market_cost"] = df["stock_price"].fillna(0) * df["shares_per_contract"].fillna(
        0
    )
    df["profit"] = df["market_cost"] - df["execution_cost"]
    df["return_on_capital"] = (
        df["profit"] / df["execution_cost"].replace(0, pd.NA)
    ).fillna(0) * 100
    return df


def main():

    refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 5, 60, 10)
    auto_refresh = st.sidebar.checkbox("Enable Auto-Refresh", value=False)

    with st.sidebar:
        st.header("Task Queue Stats")
        task_status = get_task_queue_status()
        st.metric("Queued", task_status["queued"])
        st.metric("Active", task_status["active"])
        st.metric("Completed", f"{task_status['percent_complete']} %")
        st.header("Filters")
        ticker_filter = st.text_input("Search by Ticker")
        expiration_date_filter = st.date_input("Expiration Date", value=None)
        return_filter = st.slider("% Return on Capital", -100.0, 100.0, (-100.0, 100.0))
        strike_price_filter = st.slider("Strike Price", 0.0, 1000.0, (0.0, 1000.0))
        filter_complete_data = st.checkbox("Only options with all required data")
        filter_positive_profit = st.checkbox("Only options with profit > 0")
        underlying_price_filter = st.slider(
            "Underlying Price", 0.0, 50000.0, (0.0, 50000.0)
        )

    if "data" not in st.session_state or "df" not in st.session_state:
        st.session_state["data"] = fetch_options_data()
        st.session_state["df"] = calculate_fields(st.session_state["data"])

    if auto_refresh:
        placeholder = st.empty()
        while auto_refresh:
            st.session_state["data"] = fetch_options_data()
            st.session_state["df"] = calculate_fields(st.session_state["data"])
            placeholder.dataframe(
                st.session_state["df"][
                    [
                        "ticker",
                        "underlying_ticker",
                        "ask_price",
                        "ask_size",
                        "option_price",
                        "option_position_size",
                        "execution_cost",
                        "market_cost",
                        "profit",
                        "return_on_capital",
                        "expiration_date",
                        "strike_price",
                        "stock_price",
                        "stock_timestamp",
                        "option_timestamp",
                    ]
                ]
            )
            st.metric("Total Results", len(st.session_state["df"]))
            time.sleep(refresh_interval)

    df = st.session_state["df"]

    if df.empty:
        st.warning("No data available.")
        return

    if ticker_filter:
        df = df[df["ticker"].str.contains(ticker_filter, case=False, na=False)]
    if expiration_date_filter:
        df = df[df["expiration_date"] == expiration_date_filter]
    df = df[
        (df["return_on_capital"] >= return_filter[0])
        & (df["return_on_capital"] <= return_filter[1])
    ]
    df = df[
        (df["strike_price"] >= strike_price_filter[0])
        & (df["strike_price"] <= strike_price_filter[1])
    ]
    if filter_complete_data:
        required_columns = [
            "ticker",
            "underlying_ticker",
            "strike_price",
            "contract_type",
            "shares_per_contract",
            "expiration_date",
            "delta",
            "ask_price",
            "ask_size",
            "stock_price",
        ]
        df = df.dropna(subset=required_columns)
    if filter_positive_profit:
        df = df[df["profit"] > 0]
    df = df[
        (df["stock_price"] >= underlying_price_filter[0])
        & (df["stock_price"] <= underlying_price_filter[1])
    ]

    st.metric("Total Results", len(df))

    st.dataframe(
        df[
            [
                "ticker",
                "underlying_ticker",
                "ask_price",
                "ask_size",
                "option_price",
                "option_position_size",
                "execution_cost",
                "market_cost",
                "profit",
                "return_on_capital",
                "expiration_date",
                "strike_price",
                "stock_price",
                "stock_timestamp",
                "option_timestamp",
            ]
        ]
    )

    csv = df.to_csv(index=False)
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name="filtered_options.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
