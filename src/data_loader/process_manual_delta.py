import pandas as pd
import glob
import os

def process_delta_files(input_dir='data/downloads_delta', output_file='data/processed/Delta_BTCUSD_5y.csv'):
    """
    Merges Delta Exchange monthly CSV files.
    Expected usage: Put downloaded CSVs (unzipped if needed) in 'data/downloads_delta'
    """
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Delta monthly downloads probably are .csv directly or .zip?
    # Screenshot showed "CSV" buttons, so likely .csv files directly.
    all_files = glob.glob(os.path.join(input_dir, "*.csv"))
    
    if not all_files:
        print(f"No csv files found in {input_dir}. Please place downloaded files there.")
        return

    frames = []
    
    print(f"Found {len(all_files)} files in {input_dir}")
    
    for csv_path in sorted(all_files):
        print(f"Reading {csv_path}...")
        try:
            # Delta headers usually standard.
            # We assume they are consistent.
            df = pd.read_csv(csv_path)
            frames.append(df)
        except Exception as e:
            print(f"Error reading {csv_path}: {e}")

    if not frames:
        print("No data found.")
        return

    print("Merging data...")
    full_df = pd.concat(frames, ignore_index=True)
    
    print(f"Total Rows: {len(full_df)}")
    
    # Optional: sorting by timestamp if available
    # Delta CSVs often have 'timestamp' or 'date' column.
    possible_time_cols = ['timestamp', 'date', 'time', 'Date', 'Time']
    time_col = next((c for c in possible_time_cols if c in full_df.columns), None)
    
    if time_col:
        print(f"Sorting by {time_col}...")
        # If timestamp is numeric (ms or s) or string
        # simple sort usually works enough for merging
        full_df.sort_values(by=time_col, inplace=True)
    
    full_df.to_csv(output_file, index=False)
    print(f"Merged data saved to {output_file}")

if __name__ == "__main__":
    process_delta_files()
