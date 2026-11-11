# Stock Data Visualizer (Project 3a)

Flask web version of the Project 3 stock data visualizer. Pick a stock symbol, chart type, time series and date range, and the chart shows up below the form. Stock symbols are loaded from `stocks.csv`.

## Running with Docker

1. Copy `.env.example` to `.env` and put your Alpha Vantage API key in it
2. Run `docker compose up --build`
3. Go to http://localhost:8000

## Running without Docker

```
pip install -r requirements.txt
export ALPHA_VANTAGE_API_KEY=your_key_here
python app.py
```
