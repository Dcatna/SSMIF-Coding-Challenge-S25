import pandas as pd
import yfinance as yf
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Mapping for renamed tickers (e.g., FB -> META)
ticker_map = {
    "FB": "META",
    # Add any other mappings here
}
def get_sector(yf_ticker):
    """Retrieve the sector for a given yfinance ticker via its info dict."""
    try:
        ticker_obj = yf.Ticker(yf_ticker)
        info = ticker_obj.info
        return info.get("sector", "Other")
    except Exception as e:
        return "Other"

def get_all_trades(csv_path):
    """Reads the entire trades CSV and returns it as a DataFrame."""
    df = pd.read_csv(csv_path)
    df["Date"] = pd.to_datetime(df["Date"])
    # Instead of dropping FB rows, update them to META.
    df.loc[df["Symbol"] == "FB", "Symbol"] = "META"
    df = df.sort_values("Date")
    return df

def get_yf_ticker(symbol):
    """Convert a CSV symbol to the ticker used by yfinance."""
    if symbol in ["EUR", "GBP", "JPY"]:
        return f"{symbol}USD=X"
    return ticker_map.get(symbol, symbol)
    
def get_latest_holdings(csv_path):
    df = pd.read_csv(csv_path)
    # Drop rows with "FB" since FB is mapped to META
    df = df[df["Symbol"] != "FB"]
    df["Date"] = pd.to_datetime(df["Date"])
    unique_symbols = df["Symbol"].unique()
    latest_rows = []
    for sym in unique_symbols:
        df_sym = df[df["Symbol"] == sym]
        latest_row = df_sym.loc[df_sym["Date"].idxmax()]
        latest_rows.append(latest_row)
    return pd.DataFrame(latest_rows)

def get_current_price(yf_ticker):
    """
    For a given yfinance ticker string, attempt to get today's price.
    If today's data is not available, fallback to the most recent available price
    from the ticker's full history.
    Returns (price, price_date) or (None, None) if not found.
    """
    ticker_obj = yf.Ticker(yf_ticker)
    
    # Try to get today's price (using a 1-day history)
    df_today = ticker_obj.history(period="1d")
    if not df_today.empty:
        df_today.index = pd.to_datetime(df_today.index)
        price = df_today["Close"].iloc[-1]
        price_date = df_today.index[-1]
        return price, price_date
    else:
        # Fallback: get the full history and use the last available price.
        df_full = ticker_obj.history(period="max")
        if not df_full.empty:
            df_full.index = pd.to_datetime(df_full.index)
            price = df_full["Close"].iloc[-1]
            price_date = df_full.index[-1]
            return price, price_date
    return None, None

def adjust_to_trading_day(date):
    """
    If the given date is a weekend, adjust it to the previous Friday.
    """
    if date.weekday() == 5:  # Saturday
        return date - pd.Timedelta(days=1)
    elif date.weekday() == 6:  # Sunday
        return date - pd.Timedelta(days=2)
    return date

def get_purchase_price(yf_ticker, purchase_date):
    """
    For a given yfinance ticker and a purchase date (as a datetime object),
    get the price on the adjusted purchase date (if the date is a weekend,
    we assume the purchase happened on the previous Friday).
    Returns (price, price_date) or (None, None) if not found.
    """
    adjusted_date = adjust_to_trading_day(purchase_date)
    ticker_obj = yf.Ticker(yf_ticker)
    start_date = adjusted_date.strftime("%Y-%m-%d")
    # Use a one-day window
    end_date = (adjusted_date + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    df_purchase = ticker_obj.history(start=start_date, end=end_date)
    if not df_purchase.empty:
        df_purchase.index = pd.to_datetime(df_purchase.index)
        price = df_purchase["Close"].iloc[-1]
        price_date = df_purchase.index[-1]
        return price, price_date
    return None, None

def get_daily_change(yf_ticker):
    """
    For a given yfinance ticker, get the previous trading day's close and 
    compute the daily change (today's price minus the previous day's price).
    Returns (daily_change, previous_close, previous_date) or (None, None, None) if not found.
    """
    ticker_obj = yf.Ticker(yf_ticker)
    # Retrieve data for the two most recent trading days.
    df = ticker_obj.history(period="2d")
    if len(df) >= 2:
        df.index = pd.to_datetime(df.index)
        previous_close = df["Close"].iloc[-2]
        current_close = df["Close"].iloc[-1]
        daily_change = current_close - previous_close
        previous_date = df.index[-2]
        return daily_change, previous_close, previous_date
    return None, None, None


@app.route("/sector_breakdown", methods=["GET"])
def sector_breakdown():
    """
    Endpoint to return data for a line graph of the portfolio's sector breakdown over time.
    For each day, we compute the portfolio's total value per ticker (based on cumulative trades and historical prices),
    group them by sector, and calculate the percentage breakdown.
    """
    try:
        # 1. Read all trades and compute cumulative holdings.
        df = get_all_trades("data/holdings.csv")
        df = df.sort_values("Date")
        # Pivot the data so rows are dates, columns are tickers, values are shares traded that day.
        portfolio = df.groupby(["Date", "Symbol"])["Shares"].sum().unstack(fill_value=0)
        # Get cumulative holdings over time.
        portfolio = portfolio.cumsum()
        tickers = portfolio.columns.tolist()

        # 2. Determine the date range for price history.
        start_date = portfolio.index.min().strftime("%Y-%m-%d")
        end_date = pd.Timestamp.today().strftime("%Y-%m-%d")
        # Download historical prices for all tickers in one batch.
        prices = yf.download(tickers, start=start_date, end=end_date, group_by="ticker", auto_adjust=True)
        
        # 3. Build a DataFrame of closing prices for each ticker.
        price_df = pd.DataFrame()
        for ticker in tickers:
            try:
                # When multiple tickers are downloaded, prices is a multi-index DataFrame.
                price_series = prices[ticker]["Close"]
                price_series.name = ticker
                price_df = pd.concat([price_df, price_series], axis=1)
            except Exception:
                pass  # Skip if data is missing for a ticker.
        
        # 4. Align the portfolio (cumulative shares) to the price data dates.
        portfolio = portfolio.reindex(price_df.index, method="ffill")
        # Calculate the daily value per ticker.
        value_df = portfolio * price_df

        # 5. Get sector for each ticker using yfinance info and cache it.
        sector_cache = {}
        for ticker in tickers:
            if ticker not in sector_cache:
                sector_cache[ticker] = get_sector(ticker)
        # Build a Series mapping ticker -> sector.
        sector_series = pd.Series(sector_cache)

        # 6. Group the ticker values by sector.
        sector_value_df = value_df.groupby(sector_series, axis=1).sum()
        # Calculate the total portfolio value for each day.
        total_value = sector_value_df.sum(axis=1)
        # Calculate sector percentages.
        sector_pct_df = sector_value_df.divide(total_value, axis=0) * 100

        # 7. Convert the results into a JSON-friendly format.
        breakdown_data = []
        for date, row in sector_pct_df.iterrows():
            breakdown_data.append({
                "Date": date.strftime("%Y-%m-%d"),
                "SectorBreakdown": row.to_dict()
            })
        
        return jsonify(breakdown_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/portfolio_value", methods=["GET"])
def portfolio_value():
    try:
        # 1. Read the CSV and parse dates.
        df = get_all_trades("data/holdings.csv")  # get_all_trades() already converts Date and updates FB to META.
        df = df.sort_values("Date")
        
        # 2. Pivot the data:
        #    Assume each row represents a snapshot of current holdings on that Date.
        #    For each Date and Symbol, take the last (latest) reported "Shares" value.
        portfolio = df.groupby(["Date", "Symbol"])["Shares"].last().unstack(fill_value=0)
        
        # 3. Create a continuous daily date range and forward-fill the holdings.
        all_dates = pd.date_range(start=portfolio.index.min(), end=pd.Timestamp.today(), freq="D")
        portfolio = portfolio.reindex(all_dates, method="ffill")
        
        # 4. Map each symbol to its yfinance ticker.
        mapping = {symbol: get_yf_ticker(symbol) for symbol in portfolio.columns}
        yf_tickers = list(mapping.values())
        
        # 5. Download daily price data for all tickers.
        start_date = all_dates[0].strftime("%Y-%m-%d")
        end_date = pd.Timestamp.today().strftime("%Y-%m-%d")
        prices = yf.download(
            yf_tickers,
            start=start_date,
            end=end_date,
            group_by="ticker",
            auto_adjust=True
        )
        
        if prices.empty:
            return jsonify({"error": "No price data retrieved from yfinance."}), 500
        
        # 6. Build a price DataFrame with original symbols as columns.
        price_df = pd.DataFrame()
        if isinstance(prices.columns, pd.MultiIndex):
            available_tickers = prices.columns.levels[0]
        else:
            available_tickers = yf_tickers
        
        for symbol in portfolio.columns:
            yf_ticker = mapping[symbol]
            if yf_ticker not in available_tickers:
                print(f"Ticker {yf_ticker} for symbol {symbol} not found in downloaded data.")
                continue
            try:
                series = prices[yf_ticker]["Close"]
                series.name = symbol  # Use the original symbol as the column name.
                price_df = pd.concat([price_df, series], axis=1)
            except Exception as ex:
                print(f"Error processing ticker {yf_ticker} for symbol {symbol}: {ex}")
                continue
        
        if price_df.empty:
            return jsonify({"error": "No closing price data available."}), 500
        
        # 7. Reindex price_df to the same daily date range and forward-fill.
        price_df = price_df.reindex(all_dates, method="ffill")
        
        # 8. Calculate portfolio value each day.
        portfolio_value_series = (portfolio * price_df).sum(axis=1)
        
        # 9. Format the result as JSON.
        value_data = [
            {"Date": date.strftime("%Y-%m-%d"), "PortfolioValue": value}
            for date, value in portfolio_value_series.items()
        ]
        return jsonify(value_data)
        
    except Exception as e:
        print("Error in /portfolio_value endpoint:", e)
        return jsonify({"error": str(e)}), 500




@app.route("/trades", methods=["GET"])
def trades():
    """
    Endpoint to return a table of all trades enriched with sector information.
    """
    try:
        df = get_all_trades("data/holdings.csv")
        trades_data = df.to_dict(orient="records")
        
        # Cache sector lookups to avoid duplicate API calls.
        sector_cache = {}
        for row in trades_data:
            symbol = row["Symbol"]
            yf_ticker = get_yf_ticker(symbol)
            if yf_ticker not in sector_cache:
                sector_cache[yf_ticker] = get_sector(yf_ticker)
            row["Sector"] = sector_cache[yf_ticker]
        
        return jsonify(trades_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/holdings", methods=["GET"])
def get_holdings():
    try:
        # 1. Get the latest holding row for each unique symbol.
        latest_holdings = get_latest_holdings("data/holdings.csv")
        
        results = []
        for _, row in latest_holdings.iterrows():
            symbol = row["Symbol"]
            shares = row["Shares"]
            purchase_date_dt = row["Date"]  # already a datetime object
            purchase_date = purchase_date_dt.strftime("%Y-%m-%d")
            
            yf_ticker = get_yf_ticker(symbol)
            
            # Get the current price and its date.
            current_price, current_price_date = get_current_price(yf_ticker)
            
            # Get the purchase price on the adjusted purchase date.
            purchase_price, purchase_price_date = get_purchase_price(yf_ticker, purchase_date_dt)
            
            # Get the daily change (today's price minus previous day's price)
            daily_change, prev_close, prev_date = get_daily_change(yf_ticker)
            
            result = {
                "Symbol": symbol,
                "TotalShares": shares,
                "PurchaseDate": purchase_date,
                "CurrentPrice": round(current_price, 2) if current_price is not None else None,
                "CurrentMarketValue": round(current_price * shares, 2) if current_price is not None else None,
                "CurrentPriceDate": current_price_date.strftime("%Y-%m-%d") if current_price_date is not None else None,
                "PurchasePrice": round(purchase_price, 2) if purchase_price is not None else None,
                "PurchaseMarketValue": round(purchase_price * shares, 2) if purchase_price is not None else None,
                "PurchasePriceDate": purchase_price_date.strftime("%Y-%m-%d") if purchase_price_date is not None else None,
                "DailyChange": round(daily_change, 2) if daily_change is not None else None,
                "PreviousClose": round(prev_close, 2) if prev_close is not None else None,
                "PreviousCloseDate": prev_date.strftime("%Y-%m-%d") if prev_date is not None else None
            }
            
            results.append(result)

        print(len(results))
        return jsonify(results)
    
    except Exception as e:
        print("Server Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
