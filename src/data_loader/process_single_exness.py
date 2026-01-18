import pandas as pd
import os

def process_single_csv():
    input_path = r'e:\cyptoalgotrading\data\raw\Exness_BTCUSD_2026.csv'
    output_path = r'e:\cyptoalgotrading\data\processed\exness_2026_5m.csv'
    
    print(f"Processing raw file: {input_path}")
    
    try:
        # Read in chunks as it might be large
        chunk_iterator = pd.read_csv(input_path, chunksize=1000000, names=["Exness","Symbol","Timestamp","Bid","Ask"])
        
        all_chunks = []
        for i, chunk in enumerate(chunk_iterator):
            # Skip header if it exists in data
            if chunk.iloc[0]['Exness'] == 'Exness':
                chunk = chunk.iloc[1:]
            
            chunk['Timestamp'] = pd.to_datetime(chunk['Timestamp'])
            chunk.set_index('Timestamp', inplace=True)
            
            # Convert cols to numeric
            chunk['Bid'] = pd.to_numeric(chunk['Bid'])
            chunk['Ask'] = pd.to_numeric(chunk['Ask'])
            
            chunk['mid'] = (chunk['Bid'] + chunk['Ask']) / 2
            
            # Resample to 5m
            resampled = chunk['mid'].resample('5min').ohlc()
            all_chunks.append(resampled)
            
            print(f"  Processed chunk {i+1}...")

        if all_chunks:
            print("Merging chunks...")
            full_df = pd.concat(all_chunks)
            
            # Final Cleanup Resample
            final_df = full_df.resample('5min').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last'
            }).dropna()
            
            final_df.reset_index(inplace=True)
            final_df.rename(columns={'Timestamp': 'datetime'}, inplace=True)
            
            # UTC to IST
            print("Converting to IST...")
            final_df['datetime_ist'] = final_df['datetime'] + pd.Timedelta(hours=5, minutes=30)
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            final_df.to_csv(output_path, index=False)
            print(f"SUCCESS: Saved {len(final_df)} candles to {output_path}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    process_single_csv()
