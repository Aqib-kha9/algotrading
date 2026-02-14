import pandas as pd

# 1. Load Data
file_path = "data/raw/BTCUSDm_M5_202001010000_202601121835.csv"
print(f"Loading {file_path}...")
try:
    df = pd.read_csv(file_path, sep='\t')
except:
    df = pd.read_csv(file_path)

# Parse Date
df['datetime'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'])

# Define Client Targets (Date, Type, Price)
# Copied from user request/screenshot
targets = [
    ('2026-01-01', 'Low', 87674.93),
    ('2026-01-02', 'High', 89029.84),
    ('2026-01-03', 'High', 90372),
    ('2026-01-04', 'High', 91320.54),
    ('2026-01-05', 'Low', 92827),
    ('2026-01-06', 'High', 93933.64),
    ('2026-01-07', 'Low', 92681.54),
    ('2026-01-08', 'Low', 90500),
    ('2026-01-09', 'Low', 90869.77),
    ('2026-01-10', 'Low', 90428.96),
    ('2026-01-11', 'High', 90624.45),
    ('2026-01-12', 'High', 91675), 
    ('2026-01-13', 'High', 91365.44),
    ('2026-01-14', 'High', 95681)
]

print("\n--- EXACT MATCH SEARCH ---")
print(f"{'Date':<12} | {'Type':<5} | {'Client Price':<12} | {'Found Price':<12} | {'Time Found':<20} | {'Diff':<10}")
print("-" * 90)

for date_str, type_, price in targets:
    # Filter for that specific day
    day_data = df[df['datetime'].dt.strftime('%Y-%m-%d') == date_str]
    
    if day_data.empty:
        print(f"{date_str:<12} | {type_:<5} | {price:<12} | {'NO DATA':<12} | {'-':<20} | {'-'}")
        continue

    # Find the row with the Daily High or Low depending on target
    if type_ == 'High':
        actual_val = day_data['<HIGH>'].max()
        # Find exact row closest to this high
        match_row = day_data.loc[day_data['<HIGH>'].idxmax()]
    else:
        actual_val = day_data['<LOW>'].min()
        match_row = day_data.loc[day_data['<LOW>'].idxmin()]
    
    diff = actual_val - price
    found_time = match_row['datetime'].strftime('%H:%M:%S')
    
    print(f"{date_str:<12} | {type_:<5} | {price:<12} | {actual_val:<12} | {found_time:<20} | {diff:.2f}")

print("\n--------------------------------------------------------------")
print("Note: 'Found Price' belongs to the candle at 'Time Found'.")
print("Small differences (e.g. 0.03) are likely floating point rounding.")
