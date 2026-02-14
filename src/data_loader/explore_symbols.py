import MetaTrader5 as mt5

def explore():
    if not mt5.initialize():
        print(f"initialize() failed: {mt5.last_error()}")
        return

    # 1. Check Standard Forex
    print("--- Check EURUSD ---")
    eur = mt5.symbol_info("EURUSD")
    eur_m = mt5.symbol_info("EURUSDm")
    if eur: print("EURUSD exists")
    if eur_m: print("EURUSDm exists")

    # 2. List Groups/Paths samples
    # We'll fetch all symbols and print a summary of paths
    print("\n--- Scanning Server Symbols (Sample) ---")
    all_symbols = mt5.symbols_get()
    if all_symbols:
        print(f"Total Symbols in Market Watch: {len(all_symbols)}")
        for i, s in enumerate(all_symbols):
            if i < 10:
                print(f"MW Symbol: {s.name} | Path: {s.path}")
    else:
        print("Market watch empty.")
        
    # 3. Server Wildcard scan (First 50)
    print("\n--- Scanning Server (Wildcard *) ---")
    server_symbols = mt5.symbols_get(group="*") 
    if server_symbols:
        print(f"Total Server Symbols: {len(server_symbols)}")
        # Print unique paths/groups
        paths = set()
        for s in server_symbols:
            paths.add(s.path)
            
        print(f"Unique Paths found: {len(paths)}")
        print("Sample Paths:")
        for p in sorted(list(paths))[:20]:
            print(p)
            
        # Check for Crypto path
        crypto_paths = [p for p in paths if "Crypto" in p or "Bitcoin" in p]
        print(f"\nCrypto Paths: {crypto_paths}")
        
        # Check for BTC starting symbols
        btc_starts = [s.name for s in server_symbols if s.name.startswith("BTC")]
        print(f"Symbols starting with BTC: {btc_starts[:20]}")
        
    else:
        print("Failed to fetch server symbols.")

    mt5.shutdown()

if __name__ == "__main__":
    explore()
