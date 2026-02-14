import pandas as pd

def inspect():
    path = r"e:\cyptoalgotrading\data\processed\exness_btcusd_5m_ist.csv"
    df = pd.read_csv(path)
    
    # We want to find the row where datetime_ist is close to "2026-01-07 09:45:00"
    # Let's string match to avoid parsing issues 
    match = df[df['datetime_ist'].astype(str).str.contains("2026-01-07 09:45")]
    
    if not match.empty:
        print("--- Row Matching 2026-01-07 09:45 ---")
        print(match.to_string())
    else:
        print("No string match found. Trying neighboring times.")
        neighbors = df[df['datetime_ist'].astype(str).str.contains("2026-01-07 09")]
        print(neighbors.to_string())

if __name__ == "__main__":
    inspect()
