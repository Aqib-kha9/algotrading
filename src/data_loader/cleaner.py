import pandas as pd
import os
from datetime import timedelta

def clean_data(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        return

    print(f"Cleaning {input_file}...")
    df = pd.read_csv(input_file)
    
    # Ensure datetime format
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Convert UTC to IST (UTC+5:30)
    # Note: Binance data is UTC. 
    df['datetime_ist'] = df['datetime'] + timedelta(hours=5, minutes=30)
    
    # Sort and drop duplicates
    df = df.sort_values('datetime').drop_duplicates('datetime').reset_index(drop=True)
    
    # Check for gaps (optional, just printing for now)
    df['time_diff'] = df['datetime'].diff()
    gaps = df[df['time_diff'] > timedelta(minutes=15)] # Assuming 5m or 15m candles
    if not gaps.empty:
        print(f"Found {len(gaps)} time gaps > 15 minutes.")
    
    # Save processed
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"Cleaned data saved to {output_file}. Rows: {len(df)}")

if __name__ == "__main__":
    # Auto-detect file from raw dir
    raw_dir = 'data/raw'
    files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
    if files:
        target = files[0] # Pick first for now
        clean_data(f"{raw_dir}/{target}", f"data/processed/{target}")
    else:
        print("No raw data found to clean.")
