import pandas as pd
import yfinance as yf
from datetime import timedelta
import time
# Example ticker map (adjust as needed)
ticker_map = {
    "FB": "META",  # old FB to new META
    # add others if needed
}

def get_yf_ticker(symbol):
    """
    Convert a CSV symbol to the ticker used by yfinance.
    For currencies like JPY, append "USD=X".
    """
    if symbol in ["EUR", "GBP", "JPY"]:
        return f"{symbol}USD=X"
    return ticker_map.get(symbol, symbol)

def get_price_on_date(yf_ticker, trade_date):
    """
    Given a yfinance ticker string and a trade_date (datetime),
    download data in a window (3 days before to 1 day after) and return
    the closing price on the last trading day on or before the trade_date.
    The returned value is a float (or None if no data is found).
    """
    # Define a window: from 3 days before to 1 day after the trade_date.
    start_str = (trade_date - timedelta(days=3)).strftime("%Y-%m-%d")
    end_str = (trade_date + timedelta(days=1)).strftime("%Y-%m-%d")
    
    try:
        data = yf.download(yf_ticker, start=start_str, end=end_str, auto_adjust=False, progress=False)
        if data.empty:
            return None
        data.index = pd.to_datetime(data.index)
        # Filter for dates on or before the trade_date.
        valid_data = data[data.index <= trade_date]
        if valid_data.empty:
            return None
        # Extract the last available closing price and force it to be a float.
        price = valid_data["Close"].iloc[-1]
        return float(price)
    except Exception as e:
        print(f"Error retrieving data for {yf_ticker} on {trade_date.strftime('%Y-%m-%d')}: {e}")
        return None
    
def get_sector(yf_ticker):
    """Retrieve the sector for a given yfinance ticker via its info dict."""
    try:
        ticker_obj = yf.Ticker(yf_ticker)
        info = ticker_obj.info
        return info.get("sector", "Other")
    except Exception as e:
        return "Other"
    
def enrich_csv_with_price(input_csv, output_csv):
    # Read the original CSV and parse dates.
    df = pd.read_csv(input_csv)
    df["Date"] = pd.to_datetime(df["Date"])
    
    # Update any "FB" entries to "META"
    df.loc[df["Symbol"] == "FB", "Symbol"] = "META"
    df.loc[df["Symbol"] == "EUR", "Symbol"] = "EURUSD=X"
    df.loc[df["Symbol"] == "JPY", "Symbol"] = "JPYUSD=X"
    df.loc[df["Symbol"] == "GBP", "Symbol"] = "GBPUSD=X"
    price_list = []
    
    # Group by symbol to reduce the number of API calls.
    # We'll download historical data for each unique symbol only once.
    symbols = df["Symbol"].unique()
    hist_data = {}
    
    # Download data for each symbol once.
    for symbol in symbols:
        yf_ticker = get_yf_ticker(symbol)
        # Determine the date range for this symbol in the CSV.
        symbol_dates = df.loc[df["Symbol"] == symbol, "Date"]
        min_date = symbol_dates.min()
        max_date = symbol_dates.max()
        start_str = (min_date - timedelta(days=3)).strftime("%Y-%m-%d")
        end_str = (max_date + timedelta(days=1)).strftime("%Y-%m-%d")
        try:
            data = yf.download(yf_ticker, start=start_str, end=end_str, auto_adjust=False, progress=False)
            if data.empty:
                print(f"No data found for {symbol} ({yf_ticker}).")
            else:
                data.index = pd.to_datetime(data.index)
            hist_data[symbol] = data
        except Exception as e:
            print(f"Error downloading data for {symbol} ({yf_ticker}): {e}")
            hist_data[symbol] = pd.DataFrame()
        time.sleep(1)  # small delay to help with rate limiting
    
    # For each row in the CSV, look up the price using the cached historical data.
    for idx, row in df.iterrows():
        symbol = row["Symbol"]
        trade_date = row["Date"]
        data = hist_data.get(symbol, pd.DataFrame())
        price = None


        if not data.empty:
            if trade_date in data.index:
                price = data.loc[trade_date, "Close"]
            else:
                valid_data = data[data.index <= trade_date]
                if not valid_data.empty:
                    price = valid_data["Close"].iloc[-1]
            # Ensure we convert to a float (if price is not already a scalar).
            if price is not None:
                try:
                    price = float(price)
                except Exception:
                    price = None
        if price is None:
            print(f"No price data for {symbol} on {trade_date.strftime('%Y-%m-%d')}")
        price_list.append(price)
    
    # Add the new column and save the enriched CSV.
    df["PriceOnDate"] = price_list

    unique_symbols = df["Symbol"].unique()
    sector_mapping = {}
    for symbol in unique_symbols:
        yf_ticker = get_yf_ticker(symbol)
        sector_mapping[symbol] = get_sector(yf_ticker)
    
    # Map the sector to each row based on its symbol.
    df["Sector"] = df["Symbol"].map(sector_mapping)
    df.to_csv(output_csv, index=False)
    print(f"Enriched CSV written to {output_csv}")

def getSP500Info(input_csv, output_csv):

    df = pd.read_csv(input_csv, parse_dates=["Date"])
    unique_dates = sorted(pd.to_datetime(df["Date"].unique()))

    sp_mapping = {}
    for date in unique_dates:
        start_str = (date - timedelta(days=3)).strftime("%Y-%m-%d")
        end_str = (date + timedelta(days=1)).strftime("%Y-%m-%d")
        sp_data = yf.download("^GSPC", start=start_str, end=end_str, auto_adjust=False, progress=False)
        sp_data.index = pd.to_datetime(sp_data.index)

        valid_data = sp_data[sp_data.index <= date]
        if valid_data.empty:
            sp_mapping[date.strftime("%Y-%m-%d")] = None
        else:
            sp_close = valid_data["Close"].iloc[-1]
            sp_mapping[date.strftime("%Y-%m-%d")] = float(sp_close)
        time.sleep(1)

    sp_df = pd.DataFrame(list(sp_mapping.items()), columns=["Date", "SP500Close"])
    sp_df.to_csv(output_csv, index=False)

if __name__ == "__main__":
    # Example usage
    #enrich_csv_with_price("data/holdings.csv", "data/new_holdings.csv")
    getSP500Info("data/holdings.csv", "data/S&P500Info.csv")