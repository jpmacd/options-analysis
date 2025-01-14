import streamlit as st
import pandas as pd
from sqlalchemy.sql import select
from options.database.models import Options
from options.log import log_factory
from options.database.handler import execution_handler

logger = log_factory(f"{__name__}")


def fetch_options_data():
    query = select(
        Options.ticker,
        Options.underlying_ticker,
        Options.ask_price,
        Options.ask_size,
        Options.strike_price,
        Options.contract_type,
        Options.shares_per_contract,
        Options.expiration_date,
        Options.delta,
        Options.underlying_last_trade_price,
        Options.timestamp,
    )
    result = execution_handler(query)
    return result if isinstance(result, list) else []


def calculate_fields(data):
    df = pd.DataFrame(
        data,
        columns=[
            "ticker",
            "underlying_ticker",
            "ask_price",
            "ask_size",
            "strike_price",
            "contract_type",
            "shares_per_contract",
            "expiration_date",
            "delta",
            "underlying_last_trade_price",
            "timestamp",
        ],
    )
    df["option_price"] = df["ask_price"] * 100

    df["option_position_size"] = df["ask_size"] * df["option_price"]

    df["option pps"] = df["option_price"] + (
        df["underlying_last_trade_price"] / df["shares_per_contract"]
    )
    df["market pps"] = df["underlying_last_trade_price"]
    df["execution_cost"] = (df["strike_price"] * df["shares_per_contract"]) * 100
    df["market_cost"] = df["underlying_last_trade_price"] * df["shares_per_contract"]
    df["profit"] = df["market_cost"] - df["execution_cost"]
    df["return_on_capital"] = (df["profit"] / df["execution_cost"]) * 100
    return df


def main():
    st.title("Options Dashboard")

    data = fetch_options_data()
    if not data:
        st.error("No data available")
        return

    df = calculate_fields(data)

    st.sidebar.header("Filter Options")
    ticker_filter = st.sidebar.text_input("Search by Ticker")
    expiration_date_filter = st.sidebar.date_input(
        "Expiration Date", value=None, min_value=None, max_value=None
    )
    return_filter = st.sidebar.slider(
        "% Return on Capital", min_value=-100.0, max_value=100.0, value=(-100.0, 100.0)
    )

    if ticker_filter:
        df = df[df["ticker"].str.contains(ticker_filter, case=False, na=False)]
    if expiration_date_filter:
        df = df[df["expiration_date"] == expiration_date_filter]
    df = df[
        (df["return_on_capital"] >= return_filter[0])
        & (df["return_on_capital"] <= return_filter[1])
    ]

    st.dataframe(
        df[
            [
                "ticker",
                "underlying_ticker",
                "ask_price",
                "ask_size",
                "option_price",
                "option_position_size",
                "option pps",
                "market pps",
                "execution_cost",
                "market_cost",
                "profit",
                "return_on_capital",
                "expiration_date",
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
