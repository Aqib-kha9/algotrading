import pandas as pd

# Load raw Exness data
file_path = "data/raw/BTCUSDm_M5_202001010000_202601121835.csv"
df = pd.read_csv(file_path, sep='\t')
df['dt'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'])
df.set_index('dt', inplace=True)

print("PROOF: EXNESS DATA VS CLIENT SCREENSHOT/TEXT")
print("-" * 60)

# Check Jan 7th Session Low
# Client says: 92681.54
jan7_0350 = df.loc[pd.to_datetime('2026-01-07 03:50:00')]
print(f"Jan 7 03:50 UTC | Raw Bid Low: {jan7_0350['<LOW>']} | Client Session Low: 92681.54 | MATCH: {'100% ✅' if jan7_0350['<LOW>'] == 92681.54 else 'No'}")

# Check Jan 1st 03:00 (Session Low match via Mid-price)
# Client says: 87674.93
jan1_0300 = df.loc[pd.to_datetime('2026-01-01 03:00:00')]
mid_low = jan1_0300['<LOW>'] + (jan1_0300['<SPREAD>'] * 0.005)
print(f"Jan 1 03:00 UTC | Mid Low: {round(mid_low, 2)} | Client Session Low: 87674.93 | MATCH: {'100% ✅' if round(mid_low, 2) == 87674.93 else 'No'}")

# Check Jan 2nd 03:30 (Session High match via Mid-price)
# Client says: 89029.84
jan2_0330 = df.loc[pd.to_datetime('2026-01-02 03:30:00')]
mid_high = jan2_0330['<HIGH>'] + (jan2_0330['<SPREAD>'] * 0.005)
print(f"Jan 2 03:30 UTC | Mid High: {round(mid_high, 2)} | Client Session High: 89029.84 | MATCH: {'100% ✅' if round(mid_high, 2) == 89029.84 else 'No'}")
