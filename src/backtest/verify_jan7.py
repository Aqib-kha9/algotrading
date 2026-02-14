import pandas as pd
import numpy as np

file_path = "data/raw/BTCUSDm_M5_202001010000_202601121835.csv"
try:
    df = pd.read_csv(file_path, sep='\t')
except:
    df = pd.read_csv(file_path)

df['dt'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'])
df.set_index('dt', inplace=True)

# Jan 7th
jan7 = df[df.index.date == pd.to_datetime('2026-01-07').date()]

# Session Range: 02:45 – 03:55 UTC
session = jan7[(jan7.index.time >= pd.Timestamp('02:45').time()) & (jan7.index.time <= pd.Timestamp('03:55').time())]
range_high = session['<HIGH>'].max()
range_low = session['<LOW>'].min()

print(f"--- Jan 7 Verification (2:45-3:55 UTC) ---")
print(f"Session High: {range_high}")
print(f"Session Low:  {range_low}")

# Client Levels from check_client_levels.py
client_low = 92681.54
print(f"Client Low:   {client_low}")
print(f"Diff Low:     {range_low - client_low:.2f}")

# Triggers
buy_trigger = range_high * 1.0005
sell_trigger = range_low * 0.9995
print(f"\nTriggers:")
print(f"Buy Trigger:  {buy_trigger:.2f}")
print(f"Sell Trigger: {sell_trigger:.2f}")

# Scan for Trade
trade_area = jan7[jan7.index.time > pd.Timestamp('03:55').time()]
trade_area = trade_area[trade_area.index.time <= pd.Timestamp('12:30').time()] # Entry Limit

print(f"\nScanning for entry until 12:30 UTC:")
for t, row in trade_area.iterrows():
    if row['<HIGH>'] >= buy_trigger:
        print(f"!!! BUY Entry at {t.time()} | High: {row['<HIGH>']} >= {buy_trigger:.2f}")
        break
    if row['<LOW>'] <= sell_trigger:
        print(f"!!! SELL Entry at {t.time()} | Low: {row['<LOW>']} <= {sell_trigger:.2f}")
        break
else:
    print("No trade triggered before 12:30 UTC.")
