import pandas as pd

def clear_inspect():
    path = r"e:\cyptoalgotrading\data\processed\exness_btcusd_5m_ist.csv"
    df = pd.read_csv(path)
    
    # Filter for Jan 7 2026 IST
    df['datetime_ist'] = pd.to_datetime(df['datetime_ist'], errors='coerce')
    target_time = pd.Timestamp("2026-01-07 09:45:00", tz='Asia/Kolkata')
    
    # Let's find rows around that time
    start_time = pd.Timestamp("2026-01-07 09:15:00", tz='Asia/Kolkata')
    end_time = pd.Timestamp("2026-01-07 11:00:00", tz='Asia/Kolkata')
    
    # Convert df to tz-aware for comparison if it's not
    if df['datetime_ist'].dt.tz is None:
        df['datetime_ist'] = df['datetime_ist'].dt.tz_localize('Asia/Kolkata')
    
    mask = (df['datetime_ist'] >= start_time) & (df['datetime_ist'] <= end_time)
    subset = df[mask]
    
    print("--- RAW DATA JAN 7 ---")
    for idx, row in subset.iterrows():
        print(f"Time: {row['datetime_ist']} | H: {row['high']:.2f} | L: {row['low']:.2f} | C: {row['close']:.2f}")

if __name__ == "__main__":
    clear_inspect()
