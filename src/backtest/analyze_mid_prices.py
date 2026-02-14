import pandas as pd

file_path = "data/raw/BTCUSDm_M5_202001010000_202601121835.csv"
try:
    df = pd.read_csv(file_path, sep='\t')
except:
    df = pd.read_csv(file_path)

df['dt'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'])
df.set_index('dt', inplace=True)

def analyze_mid(date_str):
    print(f"\n--- {date_str} Mid Price Analysis ---")
    day_data = df[df.index.date == pd.to_datetime(date_str).date()]
    sess = day_data.between_time('02:45', '03:55')
    
    # MT5 spread is often in points. For BTCUSD, usually multiplier is 0.01 or 0.1 depending on broker.
    # We found Jan 7 mismatch of 2.7 points. Jan 7 spread in file: ??? 
    
    for t, row in sess.iterrows():
        bid_low = row['<LOW>']
        bid_high = row['<HIGH>']
        spread_val = row['<SPREAD>']
        
        # Test multiplier 0.01 (Common for BTCUSD on Exness)
        # Mid Low = Bid Low + (Spread * 0.01 / 2)
        mid_low = bid_low + (spread_val * 0.01 / 2)
        mid_high = bid_high + (spread_val * 0.01 / 2)
        
        print(f"{t.time()} | BidL: {bid_low:.2f} | Spread: {spread_val} | MidL: {mid_low:.2f}")

analyze_mid('2026-01-01')
analyze_mid('2026-01-07')
