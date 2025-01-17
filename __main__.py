import time
import streamlit as st
import pandas as pd
from sqlalchemy.sql import select
from options.database.models import Options, OptionsQuote, Stocks, StocksQuote

from options.database.handler import execution_handler
from options.utils import get_task_queue_status
import logging

logging.getLogger("watchdog").setLevel(logging.CRITICAL)


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
    df["option_price"] = df["ask_price"].fillna(0).infer_objects(copy=False) * 100
    df["option_position_size"] = df["ask_size"].fillna(0) * df["option_price"]
    df["execution_cost"] = (
        df["strike_price"].fillna(0) * df["shares_per_contract"].fillna(0)
    ).infer_objects(copy=False) * 100
    df["market_cost"] = df["stock_price"].fillna(0) * df["shares_per_contract"].fillna(
        0
    ).infer_objects(copy=False)
    df["profit"] = df["market_cost"] - df["execution_cost"]
    df["return_on_capital"] = (
        df["profit"] / df["execution_cost"].replace(0, pd.NA)
    ).fillna(0).infer_objects(copy=False) * 100

    return df


def main():
    # Sidebar options
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

    # Initialize session state for data and dataframe
    if "data" not in st.session_state:
        st.session_state["data"] = None
    if "df" not in st.session_state:
        st.session_state["df"] = None

    # Fetch data if not already done
    if st.session_state["data"] is None:
        st.session_state["data"] = fetch_options_data()
    if st.session_state["df"] is None and st.session_state["data"]:
        st.session_state["df"] = calculate_fields(st.session_state["data"])

    # Placeholders for dynamic content
    placeholder_table = st.empty()
    placeholder_metric = st.empty()

    # Render the table and metrics
    if st.session_state["df"] is not None and not st.session_state["df"].empty:
        with placeholder_table.container():
            st.dataframe(
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
        placeholder_metric.metric("Total Results", len(st.session_state["df"]))
    else:
        placeholder_table.warning("Loading data, please wait...")
        placeholder_metric.metric("Total Results", 0)

    # Handle auto-refresh
    if auto_refresh:
        while auto_refresh:
            st.session_state["data"] = fetch_options_data()
            st.session_state["df"] = calculate_fields(st.session_state["data"])

            # Update placeholders
            if st.session_state["df"] is not None and not st.session_state["df"].empty:
                with placeholder_table.container():
                    st.dataframe(
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
                placeholder_metric.metric("Total Results", len(st.session_state["df"]))
            else:
                placeholder_table.warning("Loading data, please wait...")
                placeholder_metric.metric("Total Results", 0)

            time.sleep(refresh_interval)

    # Download button for filtered data
    if st.session_state["df"] is not None:
        csv = st.session_state["df"].to_csv(index=False)
        st.download_button(
            label="Download Filtered Data as CSV",
            data=csv,
            file_name="filtered_options.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    logging.getLogger("watchdog").disabled = True
    main()
