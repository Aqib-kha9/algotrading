import pandas as pd
import argparse

def compare_data(manual_path, client_path):
    print(f"Loading Manual Data: {manual_path}")
    # Manual Data: Tab separated, <DATE> <TIME> ...
    # Example: 2020.01.01	00:00:00	7170.00 ...
    try:
        df_manual = pd.read_csv(manual_path, sep='\t')
    except:
        # Fallback to comma if tab fails (some exports use comma)
        df_manual = pd.read_csv(manual_path)
        
    # Combine DATE and TIME
    df_manual['datetime'] = pd.to_datetime(df_manual['<DATE>'] + ' ' + df_manual['<TIME>'])
    # Assume MT5 export is in UTC or Server Time. Usually Exness is UTC+0. 
    # Let's clean up columns
    df_manual = df_manual[['datetime', '<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>']]
    df_manual.columns = ['datetime', 'open_manual', 'high_manual', 'low_manual', 'close_manual']
    
    # Client Data: Comma separated, datetime (UTC) ...
    # Example: 2021-01-01 00:00:00+00:00,28980.665 ...
    print(f"Loading Client Data: {client_path}")
    df_client = pd.read_csv(client_path)
    
    # Parse client datetime. It has timezone info (+00:00)
    df_client['datetime'] = pd.to_datetime(df_client['datetime']).dt.tz_convert(None) # Strip TZ to match manual
    
    # Merge
    print("\nMerging Data...")
    merged = pd.merge(df_manual, df_client, on='datetime', how='inner', suffixes=('_m', '_c'))
    
    print(f"Total Overlapping Rows: {len(merged)}")
    
    if len(merged) == 0:
        print("CRITICAL: No overlapping timestamps found!")
        print("Manual Range:", df_manual['datetime'].min(), "to", df_manual['datetime'].max())
        print("Client Range:", df_client['datetime'].min(), "to", df_client['datetime'].max())
        return

    # Comparisons
    diffs = pd.DataFrame()
    diffs['datetime'] = merged['datetime']
    
    attributes = ['open', 'high', 'low', 'close']
    
    print("\n--- Differences Analysis ---")
    for attr in attributes:
        manual_col = f"{attr}_manual"
        # Client file headers are 'open', 'high' etc.
        client_col = attr 
        
        diffs[f'{attr}_diff'] = merged[manual_col] - merged[client_col]
        abs_diff = diffs[f'{attr}_diff'].abs()
        
        print(f"[{attr.upper()}] Mean Diff: {abs_diff.mean():.4f} | Max Diff: {abs_diff.max():.4f}")
        
    # Check for significant mismatches > 1.0 (assuming points)
    significant_mismatch = diffs[diffs[['open_diff', 'high_diff', 'low_diff', 'close_diff']].abs().max(axis=1) > 1.0]
    
    if not significant_mismatch.empty:
        print(f"\nFound {len(significant_mismatch)} rows with differences > 1.0 point.")
        print("\nTop 5 Discrepancies:")
        print(significant_mismatch.head())
    else:
        print("\nSUCCESS: All data matches within 1.0 point tolerance!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--manual", type=str, required=True)
    parser.add_argument("--client", type=str, required=True)
    args = parser.parse_args()
    
    compare_data(args.manual, args.client)
