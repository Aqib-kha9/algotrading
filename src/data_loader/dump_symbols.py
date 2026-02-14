import MetaTrader5 as mt5

def dump_symbols():
    if not mt5.initialize():
        return

    print("Fetching symbols...")
    all_s = mt5.symbols_get(group="*") # Get ALL
    
    with open("found_symbols.txt", "w") as f:
        if all_s:
            for s in all_s:
                name_u = s.name.upper()
                path_u = s.path.upper()
                # Check for BTC or Crypto
                if "BTC" in name_u or "CRYPTO" in path_u or "BITCOIN" in path_u:
                    f.write(f"{s.name} | {s.path}\n")
    
    print("Done dumping.")
    mt5.shutdown()

if __name__ == "__main__":
    dump_symbols()
