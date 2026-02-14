import MetaTrader5 as mt5

def check_usd():
    if not mt5.initialize():
        return

    all_s = mt5.symbols_get()
    found = 0
    print("Searching for non-Stock USD symbols...")
    if all_s:
        for s in all_s:
            if "USD" in s.name and "Stock" not in s.path and "NASDAQ" not in s.path and "NYSE" not in s.path:
                print(f"Symbol: {s.name} | Path: {s.path}")
                found += 1
                if found >= 10:
                    break
    
    if found == 0:
        print("No non-stock USD symbols found.")
        
    mt5.shutdown()

if __name__ == "__main__":
    check_usd()
