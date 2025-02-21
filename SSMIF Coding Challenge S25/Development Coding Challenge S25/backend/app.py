from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import yfinance as yf
import datetime
import time

app = Flask(__name__)
CORS(app)

df = pd.read_csv("data/enriched_holdings.csv")

def getMostRecentTickerPrice():
    "Get the closing/recent ticker price from CSV"

    tickers = df["Symbol"].unique().tolist()
    data = yf.download(tickers, period="5d", interval="1d", progress=False)

    close_data = data["Close"]
    
    latest_prices = {}
    for ticker in close_data.columns:
        series = close_data[ticker].dropna()
        if not series.empty:
            latest_prices[ticker] = series.iloc[-1]
        else:
            latest_prices[ticker] = None

    return pd.Series(latest_prices) #ticker -> closing price

def getTotalChange():
    "Get total change in price for each ticker based on 2024-12-01"

    #getting total change
    today_prices = getMostRecentTickerPrice()

    base_df = df[df["Date"] == "2024-12-01"] #just hard code this
    base_prices = dict(zip(base_df["Symbol"], base_df["PriceOnDate"]))

    total_change = {}
    for ticker, current_price in today_prices.items():
        base_price = base_prices.get(ticker)
        if base_price is not None and pd.notna(base_price):
            total_change[ticker] = current_price - float(base_price)
        else:
            total_change[ticker] = None
    
    # print("Total Change (today vs. 2024-12-01):")
    # for ticker, change in total_change.items():
    #     print(f"{ticker}: {change}")
    
    return total_change

def getDailyChange():
    tickers = df["Symbol"].unique().tolist()
    data = yf.download(tickers, period="5d", interval="1d", progress=False)
    
    close_data = data["Close"]
    close_data = close_data.dropna(how="all") #drop future rows
    
    daily_changes = {}
    for ticker in tickers:
        series = close_data[ticker].dropna() #get valid closing prices
        if len(series) < 2:
            daily_changes[ticker] = None #not enough data to calc change
        else:
            daily_changes[ticker] = series.iloc[-1] - series.iloc[-2] #last two valid values
    
    # print("Daily Change (last two valid trading days) per ticker:")
    # for t, change in daily_changes.items():
    #     print(f"{t}: {change}")
    
    return daily_changes

@app.route("/current_holdings", methods=["GET"])
def current_holdings():
    """
    return current holdings (ticker, quantity, day and total change, market value, unit cost, total cost)
    """
    
    base_df = df[df["Date"] == "2024-12-01"]
    
    today_prices = getMostRecentTickerPrice()   # Series: ticker -> today's price
    daily_changes = getDailyChange()              # Dict: ticker -> daily change
    total_changes = getTotalChange()              # Dict: ticker -> total change (today vs. 2024-12-01)
    
    holdings = []
    
    for idx, row in base_df.iterrows():
        ticker = row["Symbol"]
        quantity = row["Shares"]
        unit_cost = row["PriceOnDate"]
        total_cost = quantity * unit_cost
        
        current_price = today_prices.get(ticker)
        market_value = quantity * current_price if current_price is not None else None
        
        holding = {
            "Ticker": ticker,
            "Quantity": quantity,
            "UnitCost": unit_cost,
            "TotalCost": total_cost,
            "CurrentPrice": current_price,
            "MarketValue": market_value,
            "DailyChange": daily_changes.get(ticker),
            "TotalChange": total_changes.get(ticker)
        }
        holdings.append(holding)

    return jsonify(holdings)

@app.route("/trades", methods={"GET"})
def getTrades():
    """
    Returns all of the trades from the CSV
    """

    holdings = []
    for idx, row in df.iterrows():
        ticker = row["Symbol"]
        quantity = row["Shares"]
        date = row["Date"]

        holding = {
            "Ticker" : ticker,
            "Quantity" : quantity,
            "Date" : date
        }
        holdings.append(holding)


    return jsonify(holdings)

@app.route("/portfolio_value", methods=["GET"])
def getPortfolioValue():
    """
    returns the total change in portfolio value over time (till today)
    """

    df = pd.read_csv("data/enriched_holdings.csv", parse_dates=["Date"])
    
    # Compute the value for each row (holding)
    df["PortfolioValue"] = df["Shares"] * df["PriceOnDate"]
    
    # Group by date and sum the values for all tickers on that date
    value_by_date = df.groupby("Date")["PortfolioValue"].sum().reset_index()
    value_by_date = value_by_date.sort_values("Date")
    
    # Convert the result to a list of dictionaries and return as JSON
    result = value_by_date.to_dict(orient="records")
    return jsonify(result)


if __name__ == "__main__":
    # Example usage
    app.run(debug=True)


