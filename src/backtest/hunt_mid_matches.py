import pandas as pd

file_path = "data/raw/BTCUSDm_M5_202001010000_202601121835.csv"
try:
    df = pd.read_csv(file_path, sep='\t')
except:
    df = pd.read_csv(file_path)

df['dt'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'])
df.set_index('dt', inplace=True)

target_low = 87674.93
jan1 = df[df.index.date == pd.to_datetime('2026-01-01').date()]

print(f"Searching for Mid-Low close to {target_low} on Jan 1st...")
for t, row in jan1.iterrows():
    mid_low = row['<LOW>'] + (row['<SPREAD>'] * 0.01 / 2)
    if abs(mid_low - target_low) < 0.1:
        print(f"!!! MATCH FOUND at {t.time()} UTC !!!")
        print(f"    BidLow: {row['<LOW>']} | Spread: {row['<SPREAD>']} | MidLow: {mid_low:.2f}")

# Also check for Jan 7 Low 92681.54
target_low_7 = 92681.54
jan7 = df[df.index.date == pd.to_datetime('2026-01-07').date()]
print(f"\nSearching for Mid-Low close to {target_low_7} on Jan 7th...")
for t, row in jan7.iterrows():
    mid_low = row['<LOW>'] + (row['<SPREAD>'] * 0.01 / 2)
    if abs(mid_low - target_low_7) < 0.1:
        print(f"!!! MATCH FOUND at {t.time()} UTC !!!")
        print(f"    BidLow: {row['<LOW>']} | Spread: {row['<SPREAD>']} | MidLow: {mid_low:.2f}")
