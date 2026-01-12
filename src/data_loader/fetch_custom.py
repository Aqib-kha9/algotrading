import argparse
import pandas as pd
from datetime import datetime, timedelta, timezone
import os
import sys

# Try imports
try:
    import ccxt
except ImportError:
    print("Error: ccxt not installed. Please run `pip install ccxt`")
    ccxt = None

try:
    import MetaTrader5 as mt5
except ImportError:
    print("Error: MetaTrader5 not installed. Please run `pip install MetaTrader5`")
    mt5 = None

def fetch_delta_data(symbol, days):
    """
    Fetch data from Delta Exchange using ccxt.
    """
    if not ccxt:
        return
    
    print(f"Connecting to Delta Exchange for {symbol}...")
    try:
        exchange = ccxt.delta()
    except AttributeError:
        # Fallback if specific delta constructor issues, though ccxt.delta() is standard
        print("Delta exchange not found in ccxt registry (or named differently). Checking 'delta'...")
        if 'delta' in ccxt.exchanges:
            exchange = ccxt.delta()
        else:
            print("Delta Exchange is not supported in your installed version of ccxt.")
            return

    # Timeframe 5m as per user context (from previous file usage)
    timeframe = '5m' 
    
    # Delta limit is often 2000
    limit = 1000
    
    end_time_dt = datetime.now(timezone.utc)
    start_time_dt = end_time_dt - timedelta(days=days)
    since = int(start_time_dt.timestamp() * 1000)
    end_ts = int(end_time_dt.timestamp() * 1000)
    
    print(f"Fetching {timeframe} data from {start_time_dt} to {end_time_dt}...")
    
    all_ohlcv = []
    
    while since < end_ts:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit=limit)
            if not ohlcv:
                print("No more data received.")
                break
            
            all_ohlcv.extend(ohlcv)
            
            # Update since
            last_timestamp = ohlcv[-1][0]
            since = last_timestamp + 1 # Or timeframe duration
            
            # Basic progress
            print(f"Fetched up to {datetime.fromtimestamp(last_timestamp/1000, timezone.utc)}")
            
        except Exception as e:
            print(f"Error fetching from Delta: {e}")
            break

    if not all_ohlcv:
        print("No data fetched.")
        return

    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    save_data(df, "Delta", symbol, days)

def fetch_mt5_data(symbol, days):
    """
    Fetch data from local MetaTrader 5 instance.
    """
    if not mt5:
        return

    print("Initializing MetaTrader 5...")
    if not mt5.initialize():
        print("initialize() failed, error code =", mt5.last_error())
        print("Please ensure MetaTrader 5 is installed and running.")
        return

    # Check connection
    terminal_info = mt5.terminal_info()
    if terminal_info:
        print(f"Connected to MT5 Terminal: {terminal_info.name} | Broker: {mt5.account_info().company if mt5.account_info() else 'Unknown'}")
    
    # Ensure symbol exists
    # MT5 symbols might differ (e.g., BTCUSD, BTCUSD.m, etc.)
    # We will try the exact symbol provided, then variations if not found
    selected_symbol = symbol
    if not mt5.symbol_select(selected_symbol, True):
        print(f"Symbol {symbol} not found or invisible. Trying generic 'BTCUSD'...")
        if mt5.symbol_select("BTCUSD", True):
            selected_symbol = "BTCUSD"
        elif mt5.symbol_select("BTCUSD.m", True):
            selected_symbol = "BTCUSD.m"
        else:
            print(f"Could not find symbol '{symbol}' in MT5.")
            mt5.shutdown()
            return

    print(f"Fetching data for {selected_symbol}...")
    
    # Timeframe: MT5_TIMEFRAME_M5
    tf = mt5.TIMEFRAME_M5
    
    utc_to = datetime.now(timezone.utc)
    utc_from = utc_to - timedelta(days=days)
    
    # Copy rates range
    rates = mt5.copy_rates_range(selected_symbol, tf, utc_from, utc_to)
    
    mt5.shutdown()
    
    if rates is None or len(rates) == 0:
        print("No data received from MT5.")
        return

    # Convert to DataFrame
    df = pd.DataFrame(rates)
    # MT5 returns: time, open, high, low, close, tick_volume, spread, real_volume
    # Rename time to timestamp (it is in seconds, we need ms for consistency or keep as is)
    # Our other scripts seem to use 'timestamp' in ms? Let's check existing files. 
    # fetcher.py used ms. We should standardize.
    
    df['timestamp'] = df['time'] * 1000
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    # Rename columns to standard lowercase
    # MT5 fields are already lowercase in the structured array usually, let's verify
    # They are: time, open, high, low, close, tick_volume, spread, real_volume
    # We want: timestamp, open, high, low, close, volume
    
    df.rename(columns={'tick_volume': 'volume'}, inplace=True)
    
    # Keep only standard columns
    df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume', 'datetime']]
    
    # Broker name detection for filename
    # We can't easily detect 'Exness' vs 'XM' unless we are logged in. 
    # We'll rely on the user passing --exchange argument for proper labeling, 
    # OR we use the account info company name we printed earlier.
    
    save_data(df, "MT5_Export", selected_symbol, days)


def save_data(df, source, symbol, days):
    output_dir = 'data/raw'
    os.makedirs(output_dir, exist_ok=True)
    
    # Sanitize symbol
    safe_symbol = symbol.replace('/', '').replace(':', '')
    
    filename = f"{output_dir}/{source}_{safe_symbol}_5m_{days}d.csv"
    df.to_csv(filename, index=False)
    print(f"Saved {len(df)} rows to {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch historical crypto data.')
    parser.add_argument('--exchange', type=str, required=True, choices=['delta', 'mt5'], help='Exchange to fetch from. Use mt5 for Exness/XM.')
    parser.add_argument('--symbol', type=str, default='BTC/USDT', help='Symbol to fetch (e.g. BTC/USDT for Delta, BTCUSD for MT5)')
    parser.add_argument('--days', type=int, default=1825, help='Number of days of history (default 1825 calls approx 5 years)')
    
    args = parser.parse_args()
    
    if args.exchange == 'delta':
        fetch_delta_data(args.symbol, args.days)
    elif args.exchange == 'mt5':
        # MT5 doesn't use slash usually
        symbol = args.symbol.replace('/', '') 
        fetch_mt5_data(symbol, args.days)
