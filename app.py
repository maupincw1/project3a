from datetime import date
from flask import Flask, render_template, request

from visualizer import (
    CHART_TYPES,
    TIME_SERIES,
    load_api_key,
    load_symbols,
    parse_date,
    get_stock_data,
    filter_stock_data,
    create_chart
)

app = Flask(__name__)


def validate_form(form, symbols):
    errors = []

    symbol = form.get("symbol", "").strip().upper()
    chart_type = form.get("chart_type", "").strip()
    time_series = form.get("time_series", "").strip()
    start_text = form.get("start_date", "").strip()
    end_text = form.get("end_date", "").strip()

    if not symbol:
        errors.append("Please select a stock symbol.")
    elif symbol not in symbols:
        errors.append(f"{symbol} is not a valid stock symbol.")

    if not chart_type:
        errors.append("Please select a chart type.")
    elif chart_type not in CHART_TYPES:
        errors.append("Invalid chart type selected.")

    if not time_series:
        errors.append("Please select a time series.")
    elif time_series not in TIME_SERIES:
        errors.append("Invalid time series selected.")

    start_date = None
    end_date = None

    if not start_text:
        errors.append("Please enter a start date.")
    else:
        start_date = parse_date(start_text)
        if start_date is None:
            errors.append("Start date must be in YYYY-MM-DD format.")
        elif start_date > date.today():
            errors.append("Start date cannot be in the future.")

    if not end_text:
        errors.append("Please enter an end date.")
    else:
        end_date = parse_date(end_text)
        if end_date is None:
            errors.append("End date must be in YYYY-MM-DD format.")

    if start_date and end_date and end_date < start_date:
        errors.append("End date cannot be before the start date.")

    values = {
        "symbol": symbol,
        "chart_type": chart_type,
        "time_series": time_series,
        "start_date": start_text,
        "end_date": end_text
    }

    return errors, values, start_date, end_date


@app.route("/", methods=["GET", "POST"])
def index():
    symbols = load_symbols()
    errors = []
    chart = None
    values = {}

    if not symbols:
        errors.append("Could not load stock symbols from stocks.csv.")

    if request.method == "POST":
        errors, values, start_date, end_date = validate_form(
            request.form,
            symbols
        )

        if not errors:
            api_key = load_api_key()

            if not api_key:
                errors.append("No Alpha Vantage API key was found.")
            else:
                stock_data, error = get_stock_data(
                    values["symbol"],
                    values["time_series"],
                    api_key
                )

                if error:
                    errors.append(error)
                else:
                    filtered_data = filter_stock_data(
                        stock_data,
                        start_date,
                        end_date
                    )

                    if not filtered_data:
                        errors.append(
                            "No stock data was found for the selected date range."
                        )
                    else:
                        chart = create_chart(
                            values["symbol"],
                            values["chart_type"],
                            values["time_series"],
                            filtered_data,
                            start_date,
                            end_date
                        )

    return render_template(
        "index.html",
        symbols=symbols,
        chart_types=CHART_TYPES,
        time_series=TIME_SERIES,
        values=values,
        errors=errors,
        chart=chart
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
