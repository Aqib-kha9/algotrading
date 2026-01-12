import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timezone

def check_mt5():
    print("Initializing MetaTrader 5...")
    if not mt5.initialize():
        print("initialize() failed, error code =", mt5.last_error())
        return

    # display information about the MT5 terminal
    terminal_info = mt5.terminal_info()
    if terminal_info:
        print(f"Connected to terminal: {terminal_info.name}")
        print(f"Build: {terminal_info.build}")

    # check if we are logged in
    account_info = mt5.account_info()
    if account_info:
        print(f"Broker: {account_info.company}")
        print(f"Account: {account_info.login}")
    else:
        print("Not logged into any account.")

    # Check for BTCUSD symbol
    symbols = mt5.symbols_get()
    btcusd_symbols = [s.name for s in symbols if "BTCUSD" in s.name.upper()]
    print(f"Found {len(btcusd_symbols)} BTC-related symbols: {btcusd_symbols}")

    if btcusd_symbols:
        symbol = btcusd_symbols[0]
        print(f"Checking full history for {symbol} (H1)...")
        
        utc_from = datetime(2010, 1, 1, tzinfo=timezone.utc)
        
        # Copy just 1 bar from that date (it will return the first bar >= that date)
        rates = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_H1, utc_from, 1)
        if rates is not None and len(rates) > 0:
            oldest_bar = datetime.fromtimestamp(rates[0][0], tz=timezone.utc)
            print(f"SUCCESS: Oldest available bar for {symbol} (H1): {oldest_bar}")
            print(f"Available History: {(datetime.now(timezone.utc) - oldest_bar).days / 365:.1f} years")
        else:
            print("Could not retrieve oldest H1 bar.")

    mt5.shutdown()

if __name__ == "__main__":
    check_mt5()
