import pandas as pd

# Load raw Exness data
file_path = "data/raw/BTCUSDm_M5_202001010000_202601121835.csv"
try:
    df = pd.read_csv(file_path, sep='\t')
except:
    df = pd.read_csv(file_path)

df['dt'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'])
df.set_index('dt', inplace=True)
df['mid_l'] = df['<LOW>'] + (df['<SPREAD>'] * 0.01 / 2)

jan1_sess = df[df.index.date == pd.to_datetime('2026-01-01').date()].between_time('02:45', '03:55')

print("Jan 1 Session (02:45-03:55 UTC) Mid Lows:")
print("-" * 50)
for t, row in jan1_sess.iterrows():
    print(f"{t.time()} | Bid Low: {row['<LOW>']} | Spr: {row['<SPREAD>']} | Mid Low: {row['mid_l']:.2f}")

target = 87674.93
print(f"\nSearching for exact match to {target}...")
for t, row in jan1_sess.iterrows():
    if round(row['mid_l'], 2) == target:
        print(f"FOUND MATCH at {t.time()} ✅")
    elif round(row['<LOW>'], 2) == target:
        print(f"FOUND BID LOW MATCH at {t.time()} ✅")

# Also check Jan 7th session for 92681.54
print("\nJan 7 Session Search for 92681.54...")
jan7_sess = df[df.index.date == pd.to_datetime('2026-01-07').date()].between_time('02:45', '03:55')
for t, row in jan7_sess.iterrows():
    if round(row['mid_l'], 2) == 92681.54:
        print(f"Jan 7: FOUND MID LOW MATCH at {t.time()} ✅")
    elif round(row['<LOW>'], 2) == 92681.54:
        print(f"Jan 7: FOUND BID LOW MATCH at {t.time()} ✅")
