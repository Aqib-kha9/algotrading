import pandas as pd
import zipfile
import os
import glob
from datetime import datetime, timedelta

def process_exness_zips():
    input_dir = 'data/raw'
    output_path = 'data/processed/exness_btcusd_5m_ist.csv'
    
    # Get all Exness zip files sorted
    zip_files = sorted(glob.glob(f"{input_dir}/Exness_BTCUSDm_*.zip"))
    
    if not zip_files:
        print("No Exness zip files found.")
        return

    print(f"Found {len(zip_files)} zip files: {[os.path.basename(f) for f in zip_files]}")
    
    all_resampled_chunks = []

    for zip_path in zip_files:
        print(f"Processing {os.path.basename(zip_path)}...")
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                # Assume one CSV per zip or find the largest one
                csv_files = [f for f in z.namelist() if f.endswith('.csv')]
                if not csv_files:
                    print(f"No CSV found in {zip_path}, skipping.")
                    continue
                
                target_file = csv_files[0] # Pick first one
                print(f"  Extracting & Reading {target_file}...")
                
                # Open CSV from zip
                with z.open(target_file) as f:
                    # Tick data columns usually: timestamp, bid, ask (or similar)
                    # Exness tick format might vary, but usually it is "Timestamp,Bid,Ask" or similar header
                    # We will inspect header on first chunk
                    
                    # Read in chunks to handle memory
                    chunk_iterator = pd.read_csv(f, chunksize=1000000)
                    
                    year_chunks = []
                    for i, chunk in enumerate(chunk_iterator):
                         # Standardize columns
                        chunk.columns = [c.lower() for c in chunk.columns] 
                        # Expected: timestamp (or time), bid, ask
                        
                        col_map = {c: c for c in chunk.columns}
                        # Find timestamp col
                        ts_col = next((c for c in ['timestamp', 'date', 'time'] if c in chunk.columns), None)
                        if not ts_col:
                            print("  Error: No timestamp column found.")
                            break
                            
                        chunk[ts_col] = pd.to_datetime(chunk[ts_col])
                        chunk.set_index(ts_col, inplace=True)
                        
                        # Calculate mid price
                        if 'bid' in chunk.columns and 'ask' in chunk.columns:
                            chunk['mid'] = (chunk['bid'] + chunk['ask']) / 2
                        elif 'bid' in chunk.columns:
                            chunk['mid'] = chunk['bid']
                        else:
                            print("  Error: No price columns found.")
                            break
                            
                        # Resample to 5m
                        resampled = chunk['mid'].resample('5min').ohlc()
                        year_chunks.append(resampled)
                        
                        if i % 10 == 0:
                            print(f"    Processed chunk {i}...")

                    if year_chunks:
                        # Combine year chunks and do a cleanup resample
                        year_df = pd.concat(year_chunks)
                        year_df = year_df.resample('5min').agg({
                            'open': 'first',
                            'high': 'max',
                            'low': 'min',
                            'close': 'last'
                        }).dropna()
                        all_resampled_chunks.append(year_df)
                        print(f"  Finished {os.path.basename(zip_path)}: {len(year_df)} candles.")
                        
        except Exception as e:
            print(f"Error processing {zip_path}: {e}")

    if all_resampled_chunks:
        print("Merging all years...")
        full_df = pd.concat(all_resampled_chunks)
        
        # Remove duplicates if overlaps
        full_df = full_df[~full_df.index.duplicated(keep='first')]
        full_df.sort_index(inplace=True)
        
        full_df.reset_index(inplace=True)
        full_df.rename(columns={full_df.columns[0]: 'datetime'}, inplace=True)
        
        # UTC to IST
        print("Converting to IST...")
        full_df['datetime_ist'] = full_df['datetime'] + pd.Timedelta(hours=5, minutes=30)
        
        # Save
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        full_df.to_csv(output_path, index=False)
        print(f"SUCCESS: Saved {len(full_df)} 5m candles to {output_path}")
        print(f"Range: {full_df['datetime_ist'].min()} to {full_df['datetime_ist'].max()}")
        
    else:
        print("No data processed.")

if __name__ == "__main__":
    process_exness_zips()
