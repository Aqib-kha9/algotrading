import MetaTrader5 as mt5

def find_crypto():
    if not mt5.initialize():
        print("Init failed")
        return

    print("Fetching ALL symbols...")
    all_symbols = mt5.symbols_get(group="*")
    if not all_symbols:
        print("No symbols found on server.")
        return

    print(f"Total Symbols: {len(all_symbols)}")

    # Search for BTC + USD
    btc_usd = [s.name for s in all_symbols if "BTC" in s.name.upper() and "USD" in s.name.upper()]
    print(f"BTC + USD matches: {btc_usd}")

    # Search for XAU + USD (Gold) - Control check
    xau_usd = [s.name for s in all_symbols if "XAU" in s.name.upper() and "USD" in s.name.upper()]
    print(f"XAU + USD matches: {xau_usd}")
    
    # Search for generic 'BTC' again but print paths
    btc_any = [s for s in all_symbols if "BTC" in s.name.upper()]
    print(f"Any 'BTC' count: {len(btc_any)}")
    if btc_any:
        print("First 5 'BTC' items:")
        for s in btc_any[:5]:
            print(f"Name: {s.name} | Path: {s.path}")

    mt5.shutdown()

if __name__ == "__main__":
    find_crypto()
