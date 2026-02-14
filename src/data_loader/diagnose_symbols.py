import MetaTrader5 as mt5

def check_specific_symbols():
    if not mt5.initialize():
        print(f"initialize() failed, error code = {mt5.last_error()}")
        return

    # Direct checks
    candidates = ["BTCUSD", "BTCUSDm", "BTCUSDz", "BTCUSD.a", "BTCUSD_m"]
    print("--- Direct Check ---")
    for c in candidates:
        info = mt5.symbol_info(c)
        if info:
            print(f"FOUND: {c} (Path: {info.path})")
            if not info.visible:
                print(f"  Selecting {c}...")
                if mt5.symbol_select(c, True):
                    print("  Selected.")
                else:
                    print("  Failed to select.")
        else:
            print(f"Not found: {c}")

    # Wildcard Search
    print("\n--- Wildcard Search *BTCUSD* ---")
    symbols = mt5.symbols_get(group="*BTCUSD*")
    if symbols:
        for s in symbols:
            print(f"Match: {s.name} (Path: {s.path})")
    else:
        print("No matches for *BTCUSD*")

    mt5.shutdown()

if __name__ == "__main__":
    check_specific_symbols()
