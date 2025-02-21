import pandas as pd
import yfinance as yf
import datetime
import time

df = pd.read_csv("data/enriched_holdings.csv")

def getMostRecentTickerPrice():
    "Get the closing/recent ticker price from CSV"

    tickers = df["Symbol"].unique().tolist()
    data = yf.download(tickers, period="5d", interval="1d", progress=False)
    
    # data["Close"] is a DataFrame with columns = tickers.
    close_data = data["Close"]
    
    # For each ticker, get the last non-NaN value.
    latest_prices = {}
    for ticker in close_data.columns:
        # Drop NaNs and get the last available value.
        series = close_data[ticker].dropna()
        if not series.empty:
            latest_prices[ticker] = series.iloc[-1]
        else:
            latest_prices[ticker] = None

    # Return as a Series mapping ticker -> last price.
    return pd.Series(latest_prices)

def getDayAndTotalChange():
    "Get the day and total change in price for each ticker"
    today_prices = getMostRecentTickerPrice()

    base_df = df[df["Date"] == "2024-12-01"] #just hard code this
    base_prices = dict(zip(base_df["Symbol"], base_df["PriceOnDate"]))
    print(base_prices)

    total_change = {}
    for ticker, current_price in today_prices.items():
        base_price = base_prices.get(ticker)
        if base_price is not None and pd.notna(base_price):
            total_change[ticker] = current_price - float(base_price)
        else:
            total_change[ticker] = None
    
    print("Total Change (today vs. 2024-12-01):")
    for ticker, change in total_change.items():
        print(f"{ticker}: {change}")
        
    return total_change
    
    # return total_change








if __name__ == "__main__":
    # Example usage
    getDayAndTotalChange()

