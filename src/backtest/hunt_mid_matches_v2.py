import pandas as pd

file_path = "data/raw/BTCUSDm_M5_202001010000_202601121835.csv"
try:
    df = pd.read_csv(file_path, sep='\t')
except:
    df = pd.read_csv(file_path)

df['dt'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'])
df.set_index('dt', inplace=True)

target_high = 89029.84
jan2 = df[df.index.date == pd.to_datetime('2026-01-02').date()]

print(f"Searching for Mid-High close to {target_high} on Jan 2nd...")
for t, row in jan2.iterrows():
    mid_high = row['<HIGH>'] + (row['<SPREAD>'] * 0.01 / 2)
    if abs(mid_high - target_high) < 0.1:
        print(f"!!! MATCH FOUND at {t.time()} (Raw Time) !!!")
        print(f"    BidHigh: {row['<HIGH>']} | Spread: {row['<SPREAD>']} | MidHigh: {mid_high:.2f}")

# Also check Jan 6 High 93933.64
target_high_6 = 93933.64
jan6 = df[df.index.date == pd.to_datetime('2026-01-06').date()]
print(f"\nSearching for Mid-High close to {target_high_6} on Jan 6th...")
for t, row in jan6.iterrows():
    mid_high = row['<HIGH>'] + (row['<SPREAD>'] * 0.01 / 2)
    if abs(mid_high - target_high_6) < 0.1:
        print(f"!!! MATCH FOUND at {t.time()} (Raw Time) !!!")
        print(f"    BidHigh: {row['<HIGH>']} | Spread: {row['<SPREAD>']} | MidHigh: {mid_high:.2f}")
