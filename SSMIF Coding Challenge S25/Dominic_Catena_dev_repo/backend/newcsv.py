import pandas as pd
import yfinance as yf
from datetime import timedelta
import time

#I used GPT for some of this, I dont remember the exact lines
ticker_map = {
    "FB": "META", 
}

def get_yf_ticker(symbol):
    """
        converts symbols to the correct ones
    """
    if symbol in ["EUR", "GBP", "JPY"]:
        return f"{symbol}USD=X"
    return ticker_map.get(symbol, symbol)

def get_price_on_date(yf_ticker, trade_date):
    """
    returns the closing price for a given ticker and day
    """
    start_str = (trade_date - timedelta(days=3)).strftime("%Y-%m-%d") #window for weekends
    end_str = (trade_date + timedelta(days=1)).strftime("%Y-%m-%d")
    
    try:
        data = yf.download(yf_ticker, start=start_str, end=end_str, auto_adjust=False, progress=False)
        if data.empty:
            return None
        data.index = pd.to_datetime(data.index)
        valid_data = data[data.index <= trade_date] #filter for dates on or before the trade_date
        if valid_data.empty:
            return None

        price = valid_data["Close"].iloc[-1] #last closing price 
        return float(price)
    except Exception as e:
        print(f"Error retrieving data for {yf_ticker} on {trade_date.strftime('%Y-%m-%d')}: {e}")
        return None
    
def get_sector(yf_ticker):
    """get the sector for a given ticker"""
    try:
        ticker_obj = yf.Ticker(yf_ticker)
        info = ticker_obj.info
        return info.get("sector", "Other")
    except Exception as e:
        return "Other"
    
def add_price_to_csv(input_csv, output_csv):
    """add the price for a ticker in the csv"""
    df = pd.read_csv(input_csv)
    df["Date"] = pd.to_datetime(df["Date"])
    
    df.loc[df["Symbol"] == "FB", "Symbol"] = "META" #update symbols
    df.loc[df["Symbol"] == "EUR", "Symbol"] = "EURUSD=X"
    df.loc[df["Symbol"] == "JPY", "Symbol"] = "JPYUSD=X"
    df.loc[df["Symbol"] == "GBP", "Symbol"] = "GBPUSD=X"
    price_list = []

    symbols = df["Symbol"].unique()
    hist_data = {}

    for symbol in symbols:
        yf_ticker = get_yf_ticker(symbol)
        symbol_dates = df.loc[df["Symbol"] == symbol, "Date"]
        min_date = symbol_dates.min()
        max_date = symbol_dates.max()
        start_str = (min_date - timedelta(days=3)).strftime("%Y-%m-%d")
        end_str = (max_date + timedelta(days=1)).strftime("%Y-%m-%d")
        try:
            data = yf.download(yf_ticker, start=start_str, end=end_str, auto_adjust=False, progress=False) #get data for each symbol
            if data.empty:
                print(f"No data found for {symbol} ({yf_ticker}).")
            else:
                data.index = pd.to_datetime(data.index)
            hist_data[symbol] = data
        except Exception as e:
            print(f"Error downloading data for {symbol} ({yf_ticker}): {e}")
            hist_data[symbol] = pd.DataFrame()
        time.sleep(1)
    
    for idx, row in df.iterrows(): #looking up price
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
            if price is not None:
                try:
                    price = float(price)
                except Exception:
                    price = None
        if price is None:
            print(f"No price data for {symbol} on {trade_date.strftime('%Y-%m-%d')}")
        price_list.append(price)

    df["PriceOnDate"] = price_list #add the new column

    unique_symbols = df["Symbol"].unique()
    sector_mapping = {}
    for symbol in unique_symbols:
        yf_ticker = get_yf_ticker(symbol)
        sector_mapping[symbol] = get_sector(yf_ticker)
    
    df["Sector"] = df["Symbol"].map(sector_mapping) #map sector
    df.to_csv(output_csv, index=False)
    print(f"Enriched CSV written to {output_csv}")

def getSP500Info(input_csv, output_csv):
    """Get the closing price fot the S&P500 for the unique dates in the given csv"""
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

    getSP500Info("data/holdings.csv", "data/S&P500Info.csv")