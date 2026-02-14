import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta, timezone
import os

def compare_data():
    # 1. Load Local Data
    local_path = r"e:\cyptoalgotrading\data\processed\exness_btcusd_5m_ist.csv"
    if not os.path.exists(local_path):
        print(f"File not found: {local_path}")
        return

    print(f"Loading local file: {local_path}...")
    df_local = pd.read_csv(local_path)
    
    # Parse timestamps
    # Assuming 'datetime' column in CSV is UTC, or 'datetime_ist' is IST
    # The clean_data script created 'datetime_ist' from 'datetime' + 5:30
    # Let's use the 'datetime' column (UTC) if available for easier comparison with MT5
    
    if 'datetime' in df_local.columns:
        df_local['datetime_utc'] = pd.to_datetime(df_local['datetime'], utc=True)
    elif 'datetime_ist' in df_local.columns:
         # Backward convert if necessary, but 'datetime' should be there
         df_local['datetime_utc'] = pd.to_datetime(df_local['datetime_ist'], utc=True) - timedelta(hours=5, minutes=30)
    
    # Filter for a reasonable range (e.g., year 2026 as per engine.py or last 1000 candles)
    # Let's take the last 1000 rows to be fast but representative
    df_sample = df_local.tail(1000).copy()
    
    if df_sample.empty:
        print("Local data is empty.")
        return

    start_dt = df_sample['datetime_utc'].min()
    end_dt = df_sample['datetime_utc'].max()
    
    print(f"Comparison Range (UTC): {start_dt} to {end_dt}")

    # 2. Initialize MT5
    print("Initializing MetaTrader 5...")
    
    # Try default first
    if not mt5.initialize():
        err = mt5.last_error()
        print(f"Default mt5.initialize() failed, error = {err}")
        
        # Try specific path found
        manual_path = r"C:\Program Files\MetaTrader 5\terminal64.exe"
        if os.path.exists(manual_path):
            print(f"Retrying with path: {manual_path}")
            if not mt5.initialize(path=manual_path):
                 print(f"mt5.initialize(path='{manual_path}') failed, error = {mt5.last_error()}")
                 return
        else:
            print("Could not find alternative terminal path.")
            return

    # 3. Find Symbol
    symbol_name = "BTCUSD"
    # Check if BTCUSD exists, if not try variants like BTCUSDm
    selected_symbol = None
    all_symbols = mt5.symbols_get()
    if all_symbols:
        names = [s.name for s in all_symbols]
        if symbol_name in names:
            selected_symbol = symbol_name
        else:
            # Try finding substring
            starts_with_btc = [n for n in names if n.startswith('BTCUSD')]
            if starts_with_btc:
                selected_symbol = starts_with_btc[0]
    
    if not selected_symbol:
        print("Could not find BTCUSD symbol in MT5.")
        mt5.shutdown()
        return

    print(f"Using MT5 Symbol: {selected_symbol}")
    
    # Ensure symbol is selected in Market Watch
    if not mt5.symbol_select(selected_symbol, True):
        print(f"Failed to select {selected_symbol}")
        mt5.shutdown()
        return

    # 4. Fetch Data from MT5
    # copy_rates_range(symbol, timeframe, date_from, date_to)
    # Add a small buffer to dates to ensure coverage
    range_from = start_dt - timedelta(minutes=15)
    range_to = end_dt + timedelta(minutes=15)
    
    print(f"Fetching data from MT5: {range_from} to {range_to}...")
    rates = mt5.copy_rates_range(selected_symbol, mt5.TIMEFRAME_M5, range_from, range_to)
    
    mt5.shutdown()

    if rates is None or len(rates) == 0:
        print("No data received from MT5.")
        return

    # Convert to DataFrame
    df_mt5 = pd.DataFrame(rates)
    df_mt5['time'] = pd.to_datetime(df_mt5['time'], unit='s', utc=True)
    
    # Rename columns to match
    df_mt5 = df_mt5[['time', 'open', 'high', 'low', 'close', 'tick_volume']]
    df_mt5.columns = ['datetime_utc', 'open_mt5', 'high_mt5', 'low_mt5', 'close_mt5', 'vol_mt5']

    # 5. Merge and Compare
    # Local columns: datetime, open, high, low, close, volume (assuming standard names)
    # Let's standardize local columns
    df_sample = df_sample.rename(columns={
        'open': 'open_local',
        'high': 'high_local',
        'low': 'low_local',
        'close': 'close_local',
        'volume': 'vol_local'
    })
    
    # Merge on datetime_utc
    merged = pd.merge(df_sample, df_mt5, on='datetime_utc', how='inner')
    
    print(f"\nStats:")
    print(f"Local Rows: {len(df_sample)}")
    print(f"MT5 Rows: {len(df_mt5)}")
    print(f"Matched Rows: {len(merged)}")
    
    if merged.empty:
        print("No matching timestamps found! Check timezones.")
        print(f"Local Sample: {df_sample['datetime_utc'].iloc[0]}")
        print(f"MT5 Sample: {df_mt5['datetime_utc'].iloc[0]}")
        return

    # Calculate differences
    merged['diff_open'] = merged['open_local'] - merged['open_mt5']
    merged['diff_high'] = merged['high_local'] - merged['high_mt5']
    merged['diff_low'] = merged['low_local'] - merged['low_mt5']
    merged['diff_close'] = merged['close_local'] - merged['close_mt5']
    
    # Summary
    print("\n--- Comparison Summary ---")
    print(f"Max Open Diff: {merged['diff_open'].abs().max()}")
    print(f"Max High Diff: {merged['diff_high'].abs().max()}")
    print(f"Max Low Diff: {merged['diff_low'].abs().max()}")
    print(f"Max Close Diff: {merged['diff_close'].abs().max()}")
    
    print("\nSample Mismatches (if any > 0.1):")
    mismatches = merged[merged['diff_close'].abs() > 0.1]
    if not mismatches.empty:
        print(mismatches[['datetime_utc', 'close_local', 'close_mt5', 'diff_close']].head())
    else:
        print("Perfect match (within 0.1)!")

if __name__ == "__main__":
    compare_data()
