from flask import Flask, render_template, request, jsonify, Response
import pandas as pd
from sqlalchemy.sql import select
from options.database.models import Options, OptionsQuote, Stocks, StocksQuote
from options.database.handler import execution_handler
from options.utils import get_task_queue_status
import io

app = Flask(__name__)


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
        .where(Options.shares_per_contract == 100)
        .join(OptionsQuote, Options.id == OptionsQuote.option_id, isouter=True)
        .join(Stocks, Options.underlying_ticker == Stocks.ticker, isouter=True)
        .join(StocksQuote, Stocks.id == StocksQuote.stock_id, isouter=True)
    )
    result = execution_handler(query)
    return result if result else []


import pandas as pd


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

    # Ensure numeric columns are properly handled
    numeric_columns = [
        "ask_price",
        "ask_size",
        "strike_price",
        "shares_per_contract",
        "stock_price",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Initialize calculated columns as floats
    df["option_price"] = 0.0
    df["option_position_size"] = 0.0
    df["execution_cost"] = 0.0
    df["market_cost"] = 0.0
    df["profit"] = 0.0
    df["return_on_capital"] = 0.0

    # Option price (requires ask_price)
    df.loc[df["ask_price"].notna(), "option_price"] = df["ask_price"] * 100

    # Option position size (requires ask_size and option_price)
    df.loc[
        df[["ask_size", "option_price"]].notna().all(axis=1), "option_position_size"
    ] = (df["ask_size"] * df["option_price"])

    # Execution cost (requires strike_price, shares_per_contract, and option_price > 0)
    execution_cost_mask = df[
        ["strike_price", "shares_per_contract", "option_price"]
    ].notna().all(axis=1) & (df["option_price"] > 0)
    df.loc[execution_cost_mask, "execution_cost"] = (
        df["strike_price"] * df["shares_per_contract"] + df["option_price"]
    )

    # Market cost (requires stock_price and shares_per_contract)
    market_cost_mask = df[["stock_price", "shares_per_contract"]].notna().all(axis=1)
    df.loc[market_cost_mask, "market_cost"] = (
        df["stock_price"] * df["shares_per_contract"]
    )

    # Profit (requires execution_cost and market_cost)
    profit_mask = (df["execution_cost"] > 0) & (df["market_cost"] > 0)
    df.loc[profit_mask, "profit"] = df["market_cost"] - df["execution_cost"]

    # Return on capital (requires execution_cost and profit)
    return_mask = df["execution_cost"] > 0
    df.loc[return_mask, "return_on_capital"] = df["profit"] / df["execution_cost"] * 100

    return df


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/data", methods=["POST"])
def get_data():
    start = int(request.form.get("start", 0))
    length = int(request.form.get("length", 10))
    order_column = int(request.form.get("order[0][column]", 0))
    order_dir = request.form.get("order[0][dir]", "asc")
    filter_param = request.args.get("filter", "")

    # Define column mappings
    columns = [
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
        "option_price",
        "option_position_size",
        "execution_cost",
        "market_cost",
        "profit",
        "return_on_capital",
    ]

    # Fetch and process data
    data = fetch_options_data()
    df = calculate_fields(data)

    # Apply "Show Only Profitable" filter
    if filter_param == "profitable":
        df = df[df["profit"] > 0]

    # Sort the data
    sort_column = columns[order_column]
    ascending = order_dir == "asc"
    df = df.sort_values(by=sort_column, ascending=ascending)

    # Handle pagination
    total_records = len(df)
    df_paginated = df.iloc[start : start + length]

    # Return JSON response
    return jsonify(
        {
            "recordsTotal": total_records,
            "recordsFiltered": len(df),
            "data": df_paginated.to_dict(orient="records"),
        }
    )


@app.route("/download", methods=["GET"])
def download_data():
    data = fetch_options_data()
    df = calculate_fields(data)
    csv = df.to_csv(index=False)
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=filtered_options.csv"},
    )


if __name__ == "__main__":
    app.run(debug=True)
