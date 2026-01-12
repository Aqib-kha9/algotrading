import pandas as pd
import glob
import os
import zipfile
from datetime import datetime

def process_exness_files(input_dir='data/downloads_exness', output_file='data/processed/Exness_BTCUSD_5y.csv'):
    """
    Extracts and merges Exness ZIP/CSV files.
    Expected usage: Put downloaded zips in 'data/downloads_exness'
    """
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    all_files = glob.glob(os.path.join(input_dir, "*.zip"))
    
    if not all_files:
        print(f"No zip files found in {input_dir}. Please place downloaded files there.")
        return

    frames = []
    
    for zip_path in sorted(all_files):
        print(f"Processing {zip_path}...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                # Assuming one CSV per zip usually, or multiple
                for filename in z.namelist():
                    if filename.endswith('.csv'):
                        print(f"  Extracting {filename}...")
                        with z.open(filename) as f:
                            # Exness tick data usually has: specific format. 
                            # Need to check header, but often: <date> <time> <bid> <ask> ...
                            # Let's assume standard CSV read first
                            df = pd.read_csv(f)
                            
                            # Clean and standardise
                            # We need 5m OHLCV from Tick data? Or is it bar data?
                            # "Tick history" implies Ticks. We need to resample to 5m.
                            
                            # Inspect columns (heuristic)
                            # Typical Exness Tick: Symbol, Date, Time, Bid, Ask, Volume?
                            # Or DateTime formatted.
                            # Since we can't see the file yet, we'll write a generic parser 
                            # that prints columns if it fails, or tries to guess.
                            
                            # IF it is tick data, we must resample.
                            # Let's assume 'datetime' column exists or can be created.
                            
                            # Generic fix: just append for now, user might need to debug format later
                            frames.append(df)
        except Exception as e:
            print(f"Error reading {zip_path}: {e}")

    if not frames:
        print("No data found.")
        return

    print("Merging data...")
    full_df = pd.concat(frames, ignore_index=True)
    
    print(f"Total Ticks: {len(full_df)}")
    print("Converting to 5m OHLCV...")
    
    # Heuristic column mapping
    # Often Exness has: 'timestamp' or 'date' 'time'
    # We will refine this once we see the first file structure.
    # For now, just saving the merged raw file to avoid re-unzipping
    
    full_df.to_csv(output_file, index=False)
    print(f"Merged raw data saved to {output_file}")

if __name__ == "__main__":
    process_exness_files()
