import pandas as pd

def analyze_jan7():
    # Load processed data
    path = r'e:\cyptoalgotrading\data\processed\exness_btcusd_5m_ist.csv' # Assuming this is the source used for Exness
    # Wait, previous investigation used 'delta_btcusdt...' for Verify?
    # engine.py main block ran both if they exist.
    # User asked about "Exness" data. I should check Exness data file.
    # Step 1: verify which file was used for 'exness_results.csv'
    
    # Let's assume exness path from engine.py
    path = r"e:\cyptoalgotrading\data\processed\exness_btcusd_5m_ist.csv"
    
    try:
        df = pd.read_csv(path)
    except:
        # Fallback to Delta if Exness file missing (though results exist, so file must exist)
        print("Exness file not found, trying Delta for context...")
        path = r"e:\cyptoalgotrading\data\processed\delta_btcusdt_5m_ist.csv"
        df = pd.read_csv(path)

    df['datetime_ist'] = pd.to_datetime(df['datetime_ist'], errors='coerce')
    
    # Filter Jan 7 2026
    start = pd.Timestamp('2026-01-07 09:15:00', tz='Asia/Kolkata')
    end = pd.Timestamp('2026-01-07 10:30:00', tz='Asia/Kolkata')
    
    # Ensure df matches TZ
    # If df['datetime_ist'] is string with offset, to_datetime handles it.
    # We need to normalize comparison.
    
    print(f"Data Source: {path}")
    print("--- Tracing Jan 7 Trade (Sell) ---")
    print("Entry Time: 09:45 IST")
    print("Entry Price: 92638")
    print("SL: 92916 (+278 pts)")
    print("Target: 91990 (-648 pts)")
    
    print("\n--- Candle Trace ---")
    
    # Convert string column to proper datetime for filtering
    # The csv usually has strings like "2026-01-07 09:45:00+05:30"
    df['dt_obj'] = pd.to_datetime(df['datetime_ist'], utc=True).dt.tz_convert('Asia/Kolkata')
    
    mask = (df['dt_obj'] >= start) & (df['dt_obj'] <= end)
    subset = df.loc[mask].copy()
    
    print(f"\n--- Candle Trace (Stateful) ---")
    
    state = 'waiting_for_entry'
    
    for i, row in subset.iterrows():
        t = row['dt_obj'].time()
        h = row['high']
        l = row['low']
        
        print(f"Time: {t} | High: {h} | Low: {l} | State: {state}")
        
        if state == 'waiting_for_entry':
            # Check for Sell Entry
            if l <= 92638:
                print(f">>> ENTRY TRIGGERED at {t} (Low {l} <= 92638)")
                state = 'in_trade'
                
                # Check if SL/TP hit in SAME candle
                if h >= 92916:
                    print(f"!!! SL HIT SAME CANDLE at {t} (High {h} >= 92916)")
                    break
                if l <= 91990:
                    print(f"!!! TP HIT SAME CANDLE at {t} (Low {l} <= 91990)")
                    break
                    
        elif state == 'in_trade':
            if h >= 92916:
                print(f"!!! SL HIT at {t} (High {h} >= 92916)")
                break
            if l <= 91990:
                print(f"!!! TP HIT at {t} (Low {l} <= 91990)")
                break

if __name__ == "__main__":
    analyze_jan7()
