import pandas as pd

# Load Data
file_path = "data/raw/BTCUSDm_M5_202001010000_202601121835.csv"
try:
    df = pd.read_csv(file_path, sep='\t')
except:
    df = pd.read_csv(file_path)

# Parse Date
df['datetime'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'])
df.set_index('datetime', inplace=True)

# Filter for Jan 2026
start_date = '2026-01-01'
end_date = '2026-01-14'
mask = (df.index >= start_date) & (df.index <= end_date)
df_jan = df.loc[mask]

# Resample to Daily
daily = df_jan.resample('D').agg({
    '<OPEN>': 'first',
    '<HIGH>': 'max',
    '<LOW>': 'min',
    '<CLOSE>': 'last'
})

print("\n--- Daily High / Low (Jan 1-14 2026) ---")
print(daily[['<HIGH>', '<LOW>']])

# Check specific levels from Client Screenshot
client_levels = {
    '2026-01-01': {'Low': 87674.93},
    '2026-01-02': {'High': 89029.84},
    '2026-01-03': {'High': 90372},
    '2026-01-04': {'High': 91320.54},
    '2026-01-05': {'Low': 92827},
    '2026-01-06': {'High': 93933.64},
    '2026-01-07': {'Low': 92681.54},
    '2026-01-08': {'Low': 90500},
    '2026-01-09': {'Low': 90869.77},
    '2026-01-10': {'Low': 90428.96},
    '2026-01-11': {'High': 90624.45},
    '2026-01-12': {'High': 91675, 'Low': 91675}, # Check range
    '2026-01-13': {'High': 91365.44},
    '2026-01-14': {'High': 95681}
}

print("\n--- Comparison ---")
for date_str, levels in client_levels.items():
    if date_str in daily.index:
        row = daily.loc[date_str]
        print(f"\nDate: {date_str}")
        if 'High' in levels:
            diff = row['<HIGH>'] - levels['High']
            print(f"  Range High: Client={levels['High']} | CSV={row['<HIGH>']} | Diff={diff:.2f}")
        if 'Low' in levels:
            diff = row['<LOW>'] - levels['Low']
            print(f"  Range Low:  Client={levels['Low']} | CSV={row['<LOW>']} | Diff={diff:.2f}")
    else:
        print(f"\nDate: {date_str} - NO DATA IN CSV")
