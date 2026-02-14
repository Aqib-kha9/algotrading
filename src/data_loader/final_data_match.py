import pandas as pd

# Load data
file_path = "data/raw/BTCUSDm_M5_202001010000_202601121835.csv"
df = pd.read_csv(file_path, sep='\t')
df['dt'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'])
df.set_index('dt', inplace=True)

def verify(date_str, time_str, col, expected):
    dt = pd.to_datetime(date_str + ' ' + time_str)
    row = df.loc[dt]
    mid = row[col] + (row['<SPREAD>'] * 0.01 / 2)
    mid_rounded = round(mid, 2)
    status = "100% MATCH ✅" if mid_rounded == expected else f"DIFF: {round(mid_rounded - expected, 2)}"
    print(f"{date_str} {time_str} {col} | Bid: {row[col]} | Spr: {row['<SPREAD>']} | Mid: {mid_rounded} | Expected: {expected} | {status}")

print("Verifying Exact Data Points vs Client Screenshot/Text:")
print("-" * 100)
verify('2026-01-01', '03:00', '<LOW>', 87674.93)
verify('2026-01-02', '03:30', '<HIGH>', 89029.84)
verify('2026-01-07', '03:55', '<LOW>', 92681.54)
