import ccxt
import pandas as pd
import time
from datetime import datetime, timedelta, timezone
import os

def fetch_data(symbol='BTC/USDT', timeframe='5m', start_date='2021-01-01'):
    """
    Fetches historical OHLCV data from Binance.
    """
    exchange = ccxt.delta({
        'enableRateLimit': True, 
        # 'options': {'defaultType': 'future'} # Delta default is usually fine, checking docs if needed. 
    })
    
    # Calculate start time
    start_time = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    end_time = datetime.now(timezone.utc)
    since = int(start_time.timestamp() * 1000)
    
    print(f"Fetching {symbol} {timeframe} data since {start_time}...")
    
    all_ohlcv = []
    
    while since < int(end_time.timestamp() * 1000):
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit=1000)
            if not ohlcv:
                break
            
            all_ohlcv.extend(ohlcv)
            since = ohlcv[-1][0] + 1  # Move to next timestamp
            
            # Progress print
            current_date = datetime.fromtimestamp(ohlcv[-1][0] / 1000, timezone.utc)
            print(f"Fetched up to {current_date}")
            
            # Rate limit handling is automatic in ccxt with enableRateLimit=True, but safety sleep
            # time.sleep(0.1) 
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            time.sleep(5) # Backoff
            
    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    # Save to CSV
    output_dir = 'data/raw'
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}/Delta_{symbol.replace('/', '')}_{timeframe}_{start_date}_to_now.csv"
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}. Total rows: {len(df)}")
    
    return df

if __name__ == "__main__":
    fetch_data()
