import pandas as pd
import numpy as np
import os

def prepare_delta(input_path, output_path):
    print(f"Processing Delta data from {input_path}...")
    df = pd.read_csv(input_path)
    
    # Delta usually has 'datetime' in UTC
    df['datetime'] = pd.to_datetime(df['datetime'])
    # Convert to IST (UTC+5:30)
    df['datetime_ist'] = df['datetime'] + pd.Timedelta(hours=5, minutes=30)
    
    # Ensure sorted
    df.sort_values('datetime', inplace=True)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved processed Delta data to {output_path}")

def prepare_exness(input_path, output_path, resample_rule='5min'):
    print(f"Processing Exness data from {input_path} (Resampling to {resample_rule})...")
    
    # Large file, read in chunks if necessary, but resampling tick data requires grouping.
    # For OHLC, we can process row by row or in large chunks.
    # Exness columns: Exness, Symbol, Timestamp, Bid, Ask
    
    # Use OHLC of Mid price: (Bid + Ask) / 2
    
    chunks = pd.read_csv(input_path, chunksize=1000000)
    resampled_frames = []
    
    for i, chunk in enumerate(chunks):
        print(f" Processing chunk {i+1}...")
        chunk['Timestamp'] = pd.to_datetime(chunk['Timestamp'])
        chunk['mid'] = (chunk['Bid'] + chunk['Ask']) / 2
        
        chunk.set_index('Timestamp', inplace=True)
        
        # Resample chunk to the target rule
        resampled = chunk['mid'].resample(resample_rule).ohlc()
        resampled_frames.append(resampled)
        
    print("Merging chunks and final resampling...")
    full_resampled = pd.concat(resampled_frames)
    # Final resample in case chunks split a candle
    final_ohlc = full_resampled.resample(resample_rule).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last'
    }).dropna()
    
    final_ohlc.reset_index(inplace=True)
    final_ohlc.rename(columns={'Timestamp': 'datetime'}, inplace=True)
    
    # Convert to IST
    final_ohlc['datetime_ist'] = final_ohlc['datetime'] + pd.Timedelta(hours=5, minutes=30)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_ohlc.to_csv(output_path, index=False)
    print(f"Saved resampled Exness data to {output_path}")

if __name__ == "__main__":
    # Delta
    delta_raw = r"e:\cyptoalgotrading\data\raw\Delta_BTCUSDT_5m_2021-09-01_to_now.csv"
    delta_processed = r"e:\cyptoalgotrading\data\processed\delta_btcusdt_5m_ist.csv"
    if os.path.exists(delta_raw):
        prepare_delta(delta_raw, delta_processed)
    
    # Exness
    exness_raw = r"e:\cyptoalgotrading\data\raw\Exness_BTCUSD_2021.csv"
    exness_processed = r"e:\cyptoalgotrading\data\processed\exness_btcusd_5m_ist.csv"
    if os.path.exists(exness_raw):
        prepare_exness(exness_raw, exness_processed)
