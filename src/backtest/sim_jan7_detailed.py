import pandas as pd

file_path = "data/raw/BTCUSDm_M5_202001010000_202601121835.csv"
try:
    df = pd.read_csv(file_path, sep='\t')
except:
    df = pd.read_csv(file_path)

df['dt'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'])
df.set_index('dt', inplace=True)

jan7 = df[df.index.date == pd.to_datetime('2026-01-07').date()]
sess = jan7[(jan7.index.time >= pd.Timestamp('02:45').time()) & (jan7.index.time <= pd.Timestamp('03:55').time())]
range_low = sess['<LOW>'].min()
sell_trigger = range_low * 0.9995
tp = sell_trigger * 0.9930
sl = sell_trigger * 1.0030

print(f"Sell Entry: {sell_trigger:.2f}")
print(f"TP Level:   {tp:.2f}")
print(f"SL Level:   {sl:.2f}")

found_entry = False
for t, row in jan7.iterrows():
    if not found_entry:
        if t.time() > pd.Timestamp('03:55').time() and row['<LOW>'] <= sell_trigger:
            print(f"Entry Triggered at {t.time()}")
            found_entry = True
            continue
    else:
        # Check SL first (Conservative)
        if row['<HIGH>'] >= sl:
            print(f"SL Hit at {t.time()} | High: {row['<HIGH>']} >= {sl:.2f}")
            break
        if row['<LOW>'] <= tp:
            print(f"TP Hit at {t.time()} | Low: {row['<LOW>']} <= {tp:.2f}")
            break
        if t.time() >= pd.Timestamp('13:40').time():
            print(f"Time Exit at {t.time()} | Close: {row['<CLOSE>']}")
            break
