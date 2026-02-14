import pandas as pd

file_path = "data/raw/BTCUSDm_M5_202001010000_202601121835.csv"
try:
    df = pd.read_csv(file_path, sep='\t')
except:
    df = pd.read_csv(file_path)

df['dt'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'])
df.set_index('dt', inplace=True)

def print_session(date_str):
    print(f"\n--- {date_str} Session (02:45 - 03:55 UTC) ---")
    day_data = df[df.index.date == pd.to_datetime(date_str).date()]
    sess = day_data[(day_data.index.time >= pd.Timestamp('02:45').time()) & 
                    (day_data.index.time <= pd.Timestamp('03:55').time())]
    for t, row in sess.iterrows():
        print(f"{t.time()} | H: {row['<HIGH>']:.2f} | L: {row['<LOW>']:.2f}")
    print(f"Aggregated High: {sess['<HIGH>'].max():.2f}")
    print(f"Aggregated Low:  {sess['<LOW>'].min():.2f}")

print_session('2026-01-01')
print_session('2026-01-07')
