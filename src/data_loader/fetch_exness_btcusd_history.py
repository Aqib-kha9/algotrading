import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timezone
import os
import argparse
import sys

def fetch_history(mt5_path=None, login=None, password=None, server=None):
    # 1. Initialize MT5
    print("Initializing MetaTrader 5...")
    
    init_args = {}
    if mt5_path:
        print(f"Using custom terminal path: {mt5_path}")
        init_args['path'] = mt5_path
    
    # Attempt initialize
    if not mt5.initialize(**init_args):
        err_code, err_desc = mt5.last_error()
        print(f"initialize() failed, error code = {err_code}, description = {err_desc}")
        if err_code == -6: # Authorization failed
            print("\n!!! AUTHORIZATION FAILED !!!")
            print("Please ensure 'Allow automated trading' is enabled in Tools -> Options -> Expert Advisors.")
        return

    # 2. Login (Explicit or Check)
    authorized = False
    
    # If credentials provided, try explicit login
    if login and password and server:
        print(f"Attempting explicit login for account {login} on server {server}...")
        authorized = mt5.login(login=login, password=password, server=server)
        if not authorized:
            print(f"Explicit login failed. Code: {mt5.last_error()}")
    else:
        # Check current connection
        account_info = mt5.account_info()
        if account_info:
            print(f"Connected to Account: {account_info.login} ({account_info.company})")
            authorized = True
        else:
            print("Connected to terminal, but NO ACCOUNT found (Authorization failed).")
            print("Try passing --login, --password, and --server arguments.")
            
    if not authorized:
        print("Cannot proceed without authorization.")
        mt5.shutdown()
        return

    # 3. Identify Symbol
    # Exness often uses suffix like "m" (BTCUSDm) or just BTCUSD
    symbol = "BTCUSD"
    # Try to find the exact symbol available
    found_symbol = None
    all_symbols = mt5.symbols_get()
    if all_symbols:
        names = [s.name for s in all_symbols]
        if symbol in names:
            found_symbol = symbol
        else:
            # Look for BTCUSD w/ suffix
            candidates = [n for n in names if n.startswith("BTCUSD")]
            if candidates:
                found_symbol = candidates[0] # Take first match
    
    if not found_symbol:
        print(f"BTCUSD symbol not found in MT5 Market Watch. Please add it to Market Watch manually.")
        mt5.shutdown()
        return

    print(f"Found Symbol: {found_symbol}")
    
    # Ensure symbol is selected
    if not mt5.symbol_select(found_symbol, True):
        print(f"Failed to select {found_symbol}")
        mt5.shutdown()
        return

    # 4. Define Time Range
    # Getting data from 2018 to ensure we have enough history
    # Using UTC for requests
    utc_from = datetime(2018, 1, 1, tzinfo=timezone.utc)
    utc_to = datetime.now(timezone.utc)
    
    print(f"Fetching M1 history for {found_symbol} from {utc_from} to {utc_to}...")

    # 5. Fetch Data
    rates = mt5.copy_rates_range(found_symbol, mt5.TIMEFRAME_M1, utc_from, utc_to)
    
    mt5.shutdown()

    if rates is None or len(rates) == 0:
        print("No data received!")
        return

    print(f"Received {len(rates)} bars.")

    # 6. Process and Save
    df = pd.DataFrame(rates)
    
    # Convert timestamp
    df['time'] = pd.to_datetime(df['time'], unit='s', utc=True)
    
    # Rename for consistency if needed, but keeping raw MT5 names is fine for 'raw' folder.
    # Usually: time, open, high, low, close, tick_volume, spread, real_volume
    
    output_dir = r"e:\cyptoalgotrading\data\raw\exness"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, "btcusd_m1.csv")
    
    print(f"Saving to {output_path}...")
    df.to_csv(output_path, index=False)
    print("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, help="Path to terminal64.exe", default=None)
    parser.add_argument("--login", type=int, help="Account Login ID", default=None)
    parser.add_argument("--password", type=str, help="Account Password", default=None)
    parser.add_argument("--server", type=str, help="Broker Server Name", default=None)
    args = parser.parse_args()
    
    fetch_history(mt5_path=args.path, login=args.login, password=args.password, server=args.server)
