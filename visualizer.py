import csv
import os
import requests
import pygal
from datetime import datetime


CHART_TYPES = {
    "1": "Bar",
    "2": "Line"
}

TIME_SERIES = {
    "1": "Intraday",
    "2": "Daily",
    "3": "Weekly",
    "4": "Monthly"
}


def load_api_key():
    api_key = os.environ.get("ALPHA_VANTAGE_API_KEY", "").strip()

    if api_key:
        return api_key

    try:
        with open("api_key.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return None


def load_symbols(file_name="stocks.csv"):
    symbols = []

    try:
        with open(file_name, "r", newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                symbol = row.get("Symbol", "").strip().upper()

                if symbol:
                    symbols.append(symbol)

    except (FileNotFoundError, csv.Error):
        return []

    return sorted(set(symbols))


def parse_date(date_string):
    try:
        return datetime.strptime(
            date_string.strip(),
            "%Y-%m-%d"
        ).date()
    except (ValueError, AttributeError):
        return None


def get_stock_data(symbol, time_series, api_key):
    url = "https://www.alphavantage.co/query"

    functions = {
        "1": (
            "TIME_SERIES_INTRADAY",
            "Time Series (60min)"
        ),
        "2": (
            "TIME_SERIES_DAILY",
            "Time Series (Daily)"
        ),
        "3": (
            "TIME_SERIES_WEEKLY",
            "Weekly Time Series"
        ),
        "4": (
            "TIME_SERIES_MONTHLY",
            "Monthly Time Series"
        )
    }

    function_name, data_key = functions[time_series]

    params = {
        "function": function_name,
        "symbol": symbol,
        "apikey": api_key
    }

    if time_series == "1":
        params["interval"] = "60min"

    if time_series == "2":
        params["outputsize"] = "compact"

    try:
        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

    except requests.RequestException:
        return None, "Could not connect to Alpha Vantage."

    except ValueError:
        return None, "Invalid response received from Alpha Vantage."

    if "Error Message" in data:
        return None, "Invalid stock symbol or API request."

    if "Note" in data:
        return None, "API request limit reached. Please try again later."

    if "Information" in data:
        return None, "Alpha Vantage: " + data["Information"]

    if data_key not in data:
        return None, "Stock data could not be found."

    return data[data_key], None


def filter_stock_data(
    stock_data,
    start_date,
    end_date
):
    filtered_data = []

    for timestamp, values in stock_data.items():
        try:
            data_date = datetime.strptime(
                timestamp[:10],
                "%Y-%m-%d"
            ).date()

            if start_date <= data_date <= end_date:
                filtered_data.append(
                    {
                        "timestamp": timestamp,
                        "date": data_date,
                        "open": float(values["1. open"]),
                        "high": float(values["2. high"]),
                        "low": float(values["3. low"]),
                        "close": float(values["4. close"])
                    }
                )

        except (ValueError, KeyError):
            continue

    filtered_data.sort(
        key=lambda item: item["timestamp"]
    )

    return filtered_data


def create_chart(
    symbol,
    chart_type,
    time_series,
    stock_data,
    start_date,
    end_date
):
    chart_settings = {
        "x_label_rotation": 45,
        "show_minor_x_labels": True,
        "truncate_label": -1,
        "margin_bottom": 100
    }

    if chart_type == "1":
        chart = pygal.Bar(**chart_settings)
    else:
        chart = pygal.Line(**chart_settings)

    chart.title = (
        f"Stock Data for {symbol}: "
        f"{start_date.strftime('%Y-%m-%d')} "
        f"to {end_date.strftime('%Y-%m-%d')}"
    )

    chart.x_title = "Date"
    chart.y_title = "Price ($)"

    labels = []
    open_prices = []
    high_prices = []
    low_prices = []
    close_prices = []

    for item in stock_data:
        if time_series == "1":
            labels.append(item["timestamp"])
        else:
            labels.append(item["date"].strftime("%Y-%m-%d"))

        open_prices.append(item["open"])
        high_prices.append(item["high"])
        low_prices.append(item["low"])
        close_prices.append(item["close"])

    chart.x_labels = labels

    chart.add("Open", open_prices)
    chart.add("High", high_prices)
    chart.add("Low", low_prices)
    chart.add("Close", close_prices)

    # returns the chart as a data uri so it can go in an img tag
    return chart.render_data_uri()
